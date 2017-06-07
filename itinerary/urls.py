from django.conf.urls import url

from itinerary.views import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]