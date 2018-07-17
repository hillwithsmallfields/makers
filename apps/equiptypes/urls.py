# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views


urlpatterns = [
    path('', views.public_index, name='index'),
    path('<eqty>', views.public_index, name='index')
]
