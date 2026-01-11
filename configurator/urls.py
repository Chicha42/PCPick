from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.my_builds, name='profile'),
    path('save-build/', views.save_build, name='save_build'),
    path('profile/info/', views.profile_info, name='profile_info'),
    path('build/<int:pk>/', views.build_detail, name='build_detail'),
    path('build/delete/<int:pk>', views.delete_build, name='delete_build'),
    path('profile/info/edit_profile', views.edit_profile, name='edit_profile'),
    path('profile/info/change_password/', views.change_password, name='change_password'),
]
