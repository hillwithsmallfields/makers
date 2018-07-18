# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views

app_name = 'machines'

urlpatterns = [
    path('', views.public_index, name='index'),
    path('<machine>', views.public_index, name='index')
]
