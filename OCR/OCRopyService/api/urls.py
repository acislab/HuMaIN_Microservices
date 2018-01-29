from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^$', views.ocrView, name='ocrView'),
]