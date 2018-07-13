# from https://wsvincent.com/django-custom-user-model-tutorial/

# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
]
