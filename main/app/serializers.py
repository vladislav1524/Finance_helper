from rest_framework import serializers
from .models import Goal, Expense, Income, CustomUser


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'title']


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ['amount', 'title']


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['name', 'target_amount', 'current_amount', 'status']
     