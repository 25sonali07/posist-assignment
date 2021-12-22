from django.contrib import admin
from django.urls import path, include
from landing import views

urlpatterns = [
    path('',views.home, name="home"),
    path('dashboard/',views.dashboard, name="dashboard"),
    path('signup/', views.handleSignup, name="signup"),
    path('login/', views.handleLogin, name="login"),
    path('logout/', views.handleLogout, name="logout"),
    path('channel/', views.ChannelView.as_view(), name="Channel"),
    path('post/', views.PostView.as_view(), name="Post"),
    path('channel/<int:pk>', views.openChannel, name="Open Channel"),
]