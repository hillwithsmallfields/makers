# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views

app_name = 'training'

urlpatterns = [
    path('', views.list_training, name='index'),
    path('request', views.request_training, name='request'),
    path('cancel_request', views.cancel_training_request, name='cancel'),
    # path('<who>', views.public_index, name='index')
]
