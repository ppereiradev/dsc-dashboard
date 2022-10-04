from django.urls import path, include
from . import views
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

app_name = 'accounts'

urlpatterns = [
    path('login/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path("password_reset/", views.password_reset_request, name="password_reset"),
        
    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'),
        name='password_reset_done'
    ),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='reset/done/'),
        name='password_reset_confirm'
    ),
    path('reset/MQ/set-password/reset/done/', PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete'
    ),

    path('reset/Mw/set-password/reset/done/', PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'),
        name='_password_reset_complete'
    ),
]