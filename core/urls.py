from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search', views.search, name='search'),
    path('history', views.HistoryView.as_view(), name='history'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('callback', views.callback_view, name='callback'),
]
