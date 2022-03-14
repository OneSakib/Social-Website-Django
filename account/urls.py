from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'account'

urlpatterns = [
    #     post view
    path('', views.dashboard, name='dashboard'),
    path('login', views.user_login, name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name='account/logout.html'), name='logout'),
    path('password_change/', views.password_change, name='password_change'),
    path('password_reset/', views.password_reset_request, name='password_request'),
    path('register', views.register, name='register'),
    path('edit/', views.edit, name='edit'),
    path('users/', views.user_list, name='user_list'),
    path('users/<username>/', views.user_detail, name='user_detail'),
    path('users/follow/', views.user_follow, name='user_follow')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
