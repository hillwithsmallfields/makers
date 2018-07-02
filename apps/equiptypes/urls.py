# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views


urlpatterns = [
    path('', equiptypes.public_index, name='index')
]
