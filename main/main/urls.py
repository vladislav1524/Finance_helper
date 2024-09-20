from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from app import views
from allauth.account.views import PasswordChangeView
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = [
    path('auth/', include('social_django.urls', namespace='social')),
    path('accounts/first_page_login/', views.login_with_email, name='first_page_login'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='account_login'),
    path('accounts/password/reset/', views.CustomPasswordResetView.as_view(), name='account_reset_password1'),
    path('accounts/password/change/done/', TemplateView.as_view(template_name='account/password_change_done.html'), name='account_password_change_done'),
    path('accounts/password/change/', PasswordChangeView.as_view(success_url='done/'), name='password_change'),
    path('accounts/register/', views.RegistrationView.as_view(), name='register'),
    path('accounts/password_reset/notification/', views.password_reset_notification, name='password_reset_notification'),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('api/user/financial-info/', views.UserFinancialInfoView.as_view(), name='user-financial-info'),
    path('', include('app.urls', namespace='app')),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]