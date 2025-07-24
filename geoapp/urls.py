from django.urls import path
from . import views

urlpatterns = [
    path('', views.continent_form, name='continent_form'),
    path('results/<str:continent>/', views.search_results, name='search_results'),
    path('history/', views.history, name='history'),
] 