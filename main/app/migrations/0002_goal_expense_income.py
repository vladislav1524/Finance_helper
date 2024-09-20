# Generated by Django 5.1 on 2024-09-03 14:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Название')),
                ('target_amount', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Цель (₽)')),
                ('current_amount', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('status', models.CharField(choices=[('current', 'Текущая'), ('completed', 'Завершённая')], default='current', max_length=10)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
            options={
                'verbose_name': 'Цель',
                'verbose_name_plural': 'Цели',
                'ordering': ['-status', '-date'],
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Сумма (₽)')),
                ('category', models.CharField(choices=[('supermarkets', 'Супермаркеты'), ('Restaurants and cafes', 'Рестораны и кафе'), ('health and beauty', 'Здоровье и красота'), ('clothing and accessories', 'Одежда и аксессуары'), ('Utilities, communications, Internet', 'Коммунальные услуги, связь, интернет'), ('transport', 'Транспорт'), ('car', 'машина'), ('Education', 'Образование'), ('recreation and entertainment', 'Отдых и развлечения'), ('credit/mortgage', 'Кредит/Ипотека'), ('Everything for home', 'Товары для дома'), ('Other expenses', 'Прочие расходы')], max_length=50, verbose_name='Категория')),
                ('title', models.CharField(max_length=40, verbose_name='Название')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Расход',
                'verbose_name_plural': 'Расход',
                'ordering': ['-date'],
                'indexes': [models.Index(fields=['-date'], name='app_expense_date_7cd878_idx')],
            },
        ),
        migrations.CreateModel(
            name='Income',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Сумма (₽)')),
                ('title', models.CharField(max_length=40, verbose_name='Название')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incomes', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Доход',
                'verbose_name_plural': 'Доход',
                'ordering': ['-date'],
                'indexes': [models.Index(fields=['-date'], name='app_income_date_4187a7_idx')],
            },
        ),
    ]