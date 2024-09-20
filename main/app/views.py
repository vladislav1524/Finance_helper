from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from rest_framework.response import Response
from .forms import GoalForm, GoalEditForm, IncomeForm, ExpenseForm, RegistrationForm, EmailForm    
from .models import Expense, Income, Goal, CustomUser
from .serializers import ExpenseSerializer, IncomeSerializer, GoalSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from allauth.account.views import LoginView, PasswordResetView
from decimal import Decimal
import requests
import xml.etree.ElementTree as ET
from django.core.cache import cache
from .tasks import send_email_task
import json
from django.conf import settings


# главная страница
@login_required
def index(request):
    # курсы валюты
    rates = cache.get('currency_rates')
    if rates is None:
        url_rates = "https://www.cbr-xml-daily.ru/daily_utf8.xml"
        response = requests.get(url_rates)
        root = ET.fromstring(response.content)

        usd_rate = None
        eur_rate = None

        for valute in root.findall('Valute'):
            char_code = valute.find('CharCode').text
            value = valute.find('Value').text
            if char_code == 'USD':
                usd_rate = value.replace(',', '.')
            elif char_code == 'EUR':
                eur_rate = value.replace(',', '.')

        usd_rate = float(usd_rate) if usd_rate else None
        eur_rate = float(eur_rate) if eur_rate else None
        cache.set('currency_rates', {'usd_rate': usd_rate, 'eur_rate': eur_rate}, timeout=3600)
    else:
        usd_rate = rates['usd_rate']
        eur_rate = rates['eur_rate']

    user = request.user

    # Кэширование доходов
    incomes_cache_key = f'incomes_{user.id}'
    incomes = cache.get(incomes_cache_key)
    if incomes is None:
        incomes = Income.objects.filter(user=user, date__gte=timezone.now() - timezone.timedelta(days=30))
        cache.set(incomes_cache_key, incomes, timeout=3600)

    # Кэширование расходов
    expenses_cache_key = f'expenses_{user.id}'
    expenses = cache.get(expenses_cache_key)
    if expenses is None:
        expenses = Expense.objects.filter(user=user, date__gte=timezone.now() - timezone.timedelta(days=30))
        cache.set(expenses_cache_key, expenses, timeout=3600)

    # Кэширование транзакций
    transactions_cache_key = f'transactions_{user.id}'
    transactions = cache.get(transactions_cache_key)
    if transactions is None:
        transactions = list(incomes) + list(expenses)
        transactions = sorted(transactions, key=lambda x: x.date, reverse=True)
        cache.set(transactions_cache_key, transactions, timeout=3600)

    # Кэширование целей
    current_goal = Goal.objects.filter(status='current', user=user).first()
    goals_cache_key = f'goals_{user.id}'
    goals = cache.get(goals_cache_key)
    if goals is None:
        goals = Goal.objects.filter(user=user).exclude(id=current_goal.id) if current_goal else Goal.objects.filter(user=user)
        cache.set(goals_cache_key, goals, timeout=3600)

    # финансовый совет нейросети
    ai_text = None
    if request.method == 'POST':
        
        ai_cache_key = f'ai_advice_{request.user.id}'
        cached_ai_response = cache.get(ai_cache_key)

        if cached_ai_response is None:
            url_ai = "https://api.theb.ai/v1/chat/completions"
            api_key = settings.API_THEB_KEY # Theb - сервис с ai
            expenses_for_ai = {}
            for expense in expenses:
                expenses_for_ai[expense.title] = {'сумма траты': expense.amount,
                                                'категория траты': expense.category,
                                                'дата и время': expense.date}
            incomes_for_ai = {}
            for income in incomes:
                incomes_for_ai[income.title] = {'сумма дохода': income.amount,
                                                'дата и время': income.date}

            content = f"(отвечай на русском + размер сообщения до 70 слов) Дай мне финансовый совет, исходя из переданных мною данных (проанализируй всё: и даты, и категории покупок, и названия покупок и доходов):" \
                    f" Я нахожусь в России, моя валюта - рубль. Мои траты за последние 30 дней - {expenses_for_ai}," \
                    f" Мои доходы за последние 30 дней - {incomes_for_ai}," 
            if current_goal:
                content += f" сейчас моя цель накопления - '{current_goal.name}' ({current_goal.target_amount}). Дай совет: где мне лучше сэкономить и каким образом, где лучше заработать и другое..."
                    
            
            payload = json.dumps({
                "model": "theb-ai",
                "messages": [{"role": "user", "content": content}],
                "stream": False,
                "model_params": {"temperature": 1}
            })

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            if incomes_for_ai or expenses_for_ai:
                response = requests.post(url_ai, headers=headers, data=payload)
                if response.status_code != 200:
                    ai_text = f"Ошибка запроса: {response.status_code}, {response.text} \n (у меня денег на балансе нет)"
                else:
                    try:
                        ai_response_json = response.json()
                        ai_text = ai_response_json['choices'][0]['message']['content']
                        cache.set(ai_cache_key, ai_text, timeout=86400) # 24 часа
                    except requests.exceptions.JSONDecodeError:
                        ai_text = f"Ошибка декодирования JSON: {response.text}"
            else:
                ai_text = "Недостаточно данных для ответа"
        else:

            ai_text = cached_ai_response
        if not ai_text:
            ai_text = 'Определите свою финансовую цель и создайте бюджет, в котором учтены все доходы и расходы. \n Убедитесь, что вы откладываете небольшую сумму ежемесячно на сбережения, даже если это всего 10%. \nИспользуйте высокодоходные счета или инвестиционные инструменты для накоплений. \nРегулярно пересматривайте свои финансы, чтобы оставаться на правильном пути к достижению цели. \nГлавное — постоянство и дисциплина.'
            ai_text += '\n(совет меняется только раз в 24 часа)'

    # информация для постраения диаграммы по категориям трат
    category_totals = {}

    for expense in expenses:
        category = expense.get_category()
        if expense.get_category in category_totals:
            category_totals[category] += int(expense.amount)
        else:
            category_totals[category] = int(expense.amount)

    return render(request, 'main/index.html', {
        'transactions': transactions,
        'incomes': incomes,
        'expenses': expenses,
        'goals': goals,
        'current_goal': current_goal,
        'usd_rate': usd_rate,
        'eur_rate': eur_rate,
        'ai_text': ai_text,
        'category_totals': category_totals,
    })


# crud для доходов, расходов и целей
# create
@login_required
def add_entity(request, form_class, template_name, transaction_type):
    if request.method == 'POST':
        form = form_class(request.POST, user=request.user)
        if form.is_valid():
            entity = form.save()
            current_goal = Goal.objects.filter(user=request.user, status='current').first()
            if current_goal:
                if transaction_type == 'income':
                    current_goal.update_current_amount_on_income(entity.amount)
                else:
                    current_goal.update_current_amount_on_expense(entity.amount)
            cache.delete(f'incomes_{request.user.id}')
            cache.delete(f'expenses_{request.user.id}')
            cache.delete(f'transactions_{request.user.id}')
            return redirect('app:index')
    else:
        form = form_class()
    return render(request, template_name, {'form': form})


def add_income(request):
    return add_entity(request, IncomeForm, 'main/transaction/add_income.html',
                       transaction_type='income')

def add_expense(request):
    return add_entity(request, ExpenseForm, 'main/transaction/add_expense.html',
                       transaction_type='expense')


@login_required
def add_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            cache.delete(f'goals_{request.user.id}')
            return redirect('app:index')
    else:
        form = GoalForm()
    return render(request, 'main/goal/add.html', {'form': form})


# update
@login_required
def edit_entity(request, entity_id, model, form_class, template_name, transaction_type):
    entity = get_object_or_404(model, id=entity_id, user=request.user)
    original_amount = entity.amount
    if request.method == 'POST':
        form = form_class(request.POST, instance=entity, user=request.user)
        if form.is_valid():
            entity = form.save()
            current_goal = Goal.objects.filter(user=request.user, status='current').first()
            if current_goal:
                if entity.date >= current_goal.date:
                    if transaction_type == 'income':
                        current_goal.update_current_amount_on_income(entity.amount - original_amount)
                    elif transaction_type == 'expense':
                        current_goal.update_current_amount_on_expense(entity.amount - original_amount)
            cache.delete(f'incomes_{request.user.id}')
            cache.delete(f'expenses_{request.user.id}')
            cache.delete(f'transactions_{request.user.id}')
            return redirect('app:index')
    else:
        form = form_class(instance=entity)
    return render(request, template_name, {'form': form,
                                           'entity': entity})


def edit_income(request, transaction_id):
    return edit_entity(request, transaction_id, Income, IncomeForm,
                         'main/transaction/edit_income.html', transaction_type='income')

def edit_expense(request, transaction_id):
    return edit_entity(request, transaction_id, Expense, ExpenseForm,
                         'main/transaction/edit_expense.html', transaction_type='expense')

@login_required
def edit_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        form = GoalEditForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            cache.delete(f'goals_{request.user.id}')
            return redirect('app:index')
    else:
        form = GoalEditForm(instance=goal)
    return render(request, 'main/goal/edit.html', {'form': form,
                                                   'goal': goal})


# delete
@login_required
def delete_entity(request, entity_id, model, template_name, transaction_type):
    entity = get_object_or_404(model, id=entity_id, user=request.user)
    if request.method == 'POST':
        current_goal = Goal.objects.filter(user=request.user, status='current').first()
        if current_goal:
            if transaction_type == 'income':
                if entity.date >= current_goal.date: 
                    current_goal.update_current_amount_on_income(-entity.amount)
            elif transaction_type == 'expense':
                if entity.date >= current_goal.date: 
                    current_goal.update_current_amount_on_expense(-entity.amount)
        entity.delete()
        cache.delete(f'incomes_{request.user.id}')
        cache.delete(f'expenses_{request.user.id}')
        cache.delete(f'transactions_{request.user.id}')
        return redirect('app:index')
    return render(request, template_name, {'entity': entity})


def delete_income(request, transaction_id):
    return delete_entity(request, transaction_id,
                          Income, 'main/transaction/confirm_delete_income.html',
                            transaction_type='income')

def delete_expense(request, transaction_id):
    return delete_entity(request, transaction_id,
                          Expense, 'main/transaction/confirm_delete_expense.html',
                            transaction_type='expense')

@login_required
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        goal.delete()
        cache.delete(f'goals_{request.user.id}')
        return redirect('app:index')
    return render(request, 'main/goal/confirm_delete.html', {'goal': goal})


# асинхронная отправка email для восстановления пароля
class CustomPasswordResetView(PasswordResetView):
    def send_mail(self, template_name, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None, extra_email_context=None):
        subject = self.get_subject(subject_template_name, context)
        message = self.render_mail(email_template_name, context, from_email, to_email, html_email_template_name, extra_email_context)

        # Отправка письма асинхронно
        send_email_task.delay_on_commit(subject, message, from_email, [to_email])


# api
class UserFinancialInfoView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CustomUser.objects.all()
    
    def get(self, request, *args, **kwargs):
        response_data = [] 
        
        users = self.get_queryset()
        for user in users:
            expenses = user.expenses.all()
            total_expenses = sum(expense.amount for expense in expenses)
            
            incomes = user.incomes.all()
            total_incomes = sum(income.amount for income in incomes)

            current_goal = user.goals.filter(status='current').first() 
            goals_without_current = user.goals.exclude(id=current_goal.id) if current_goal else user.goals.all()
            last_goal = goals_without_current.first()
            
            user_data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                },
                'total_expenses': total_expenses,
                'total_incomes': total_incomes,
                'current_goal': {
                    "name": current_goal.name,
                    "current_amount": current_goal.current_amount,
                    "target_amount": current_goal.target_amount,
                    "status": current_goal.status,
                    } if current_goal else None ,
                'last_goal': {
                    "name": last_goal.name,
                    "current_amount": last_goal.current_amount,
                    "target_amount": last_goal.target_amount,
                    "status": last_goal.status,
                    } if last_goal else None
                }
            response_data.append(user_data) 
        
        return Response(response_data)

    
# auth
class RegistrationView(CreateView):
    template_name = 'account/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('app:index')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            form.add_error('email', 'Пользователь с таким адресом электронной почты уже существует.')
            return self.form_invalid(form)
        
        user = form.save()

        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return HttpResponseRedirect(self.success_url)


def login_with_email(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            User = get_user_model()  # Получаем модель пользователя

            try:
                user = User.objects.get(email=email)
                # Проверяем, зарегистрирован ли пользователь через социальную сеть
                if user.social_auth.exists():
                    return redirect('password_reset_notification')
                else:
                    return redirect(f"{reverse('account_login')}?email={email}")
            except User.DoesNotExist:
                error_message = 'Пользователь с таким email не найден'
                form.add_error('email', error_message)
    else:
        form = EmailForm()

    return render(request, 'account/first_page_login.html', {'form': form})


def password_reset_notification(request):
    return render(request, 'account/password_reset_notification.html')


class CustomLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        email = request.GET.get('email', '')
        context = self.get_context_data()
        context['email'] = email
        return self.render_to_response(context)

    def form_invalid(self, form):
        email = self.request.POST.get('login', '')
        return self.render_to_response(self.get_context_data(form=form, email=email))
    
# def login_view(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username_or_email = form.cleaned_data['username_or_email']
#             password = form.cleaned_data['password']
#             users = User.objects.filter(username=username_or_email)
#             if users.exists():
#                 if users.count() > 1:
#                     form.add_error('username_or_email', 'Найдено несколько аккаунтов с этим именем. Если вы зарегистрированы через VK или Google, войдите через соответствующие кнопки ниже.')
#                     return render(request, 'main/registration/login.html', {'form': form}) 
#                 else:
#                     user = authenticate(request, username=username_or_email, password=password)
#             else:
#                 user = None

#             if user is None:
#                 users = User.objects.filter(email=username_or_email)

#                 if users.exists():
#                     if users.count() > 1:
#                         form.add_error('username_or_email', 'Найдено несколько аккаунтов с этой почтой. Если вы зарегистрированы через VK или Google, войдите через соответствующие кнопки ниже.')
#                         return render(request, 'main/registration/login.html', {'form': form}) 
#                     user = users.first()
#                 else:
#                     user = None
            
#             if user is not None:
#                 login(request, user, backend='django.contrib.auth.backends.ModelBackend')
#                 return redirect('app:index')
#             else:
#                 form.add_error(None, 'Неверные логин/почта или пароль')
#     else:
#         form = LoginForm()
    
#     return render(request, 'main/registration/login.html', {'form': form})
