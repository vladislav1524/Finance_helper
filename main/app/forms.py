from django import forms
from .models import Expense, Income, Goal, CustomUser
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# форма регистрации
class RegistrationForm(UserCreationForm):
    username = forms.CharField(required=True, max_length=20, label='Имя пользователя')
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    

# форма добавления доходов
class IncomeForm(forms.ModelForm):
        
    class Meta:
        model = Income
        fields = ('title', 'amount')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        amount = str(amount).replace(',', '.')
        
        try:
            amount = Decimal(amount)  
        except (ValueError, InvalidOperation):
            raise ValidationError("Введите корректное число для суммы дохода.")
        if amount < 0:
            raise ValidationError("Сумма дохода не может быть отрицательной.")
        if amount == 0:
            raise ValidationError("Сумма должна быть больше 0")
        return amount

    def save(self, commit=True):
        income = super().save(commit=False)
        if not self.instance.pk:  
            income.user = self.user
        if commit:
            income.save()
        return income


class EmailForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254)


# форма добавления расходов
class ExpenseForm(forms.ModelForm):
        
    class Meta:
        model = Expense
        fields = ('title', 'amount', 'category')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 0:
            raise ValidationError("Сумма расхода не может быть отрицательной.")
        if amount == 0:
            raise ValidationError("Сумма расхода не может быть равна нулю.")
        return amount

    def save(self, commit=True):
        expense = super().save(commit=False)
        if not self.instance.pk:  
            expense.user = self.user
        if commit:
            expense.save()
        return expense
    

# форма добавления новой цели накопления
class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ('name', 'target_amount')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_target_amount(self):
        target_amount = self.cleaned_data.get('target_amount')

        if target_amount < 0:
            raise ValidationError("Сумма цели не может быть отрицательной.")
        elif target_amount == 0:
            raise ValidationError("Сумма цели не может быть равна нулю.")
        return target_amount

    def save(self, commit=True):
        goal = super().save(commit=False)
        if not self.instance.pk:   # Если это новая цель
            goal.user = self.user
        if commit:
            goal.save()
        return goal
    
class GoalEditForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        goal = super().save(commit=False)
        if commit:
            goal.save()
        return goal
    

class EmailForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254)
