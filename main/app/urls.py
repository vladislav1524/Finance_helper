from django.urls import path
from django.views.generic import TemplateView
from . import views


app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', TemplateView.as_view(template_name='main/about.html'), name='about'),
    path('goal/add/', views.add_goal, name='goal_add'),
    path('income/add/', views.add_income, name='income_add'),
    path('expense/add/', views.add_expense, name='expense_add'),
    path('goal/edit/<int:goal_id>/', views.edit_goal, name='goal_edit'),
    path('income/edit/<int:transaction_id>/',
          views.edit_income,
          name='income_edit'),
    path('expense/edit/<int:transaction_id>/',
          views.edit_expense,
          name='expense_edit'),
    path('goal/delete/<int:goal_id>/', views.delete_goal, name='goal_delete'),
    path('income/delete/<int:transaction_id>/',
          views.delete_income,
          name='income_delete'),
    path('expense/delete/<int:transaction_id>/',
          views.delete_expense,
          name='expense_delete'),
]
