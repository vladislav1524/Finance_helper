from django.contrib import admin
from .models import Expense, Income, Goal, CustomUser



@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'category', 'title', 'date']
    list_filter = ['category', 'date']
    date_hierarchy = 'date'
    search_fields = ['title', 'category']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'title', 'date']
    list_filter = ['date']
    date_hierarchy = 'date'
    search_fields = ['title']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_amount', 'target_amount']
    list_filter = ['name', 'target_amount']
    search_fields = ['name']
