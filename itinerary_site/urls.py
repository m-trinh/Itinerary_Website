"""itinerary_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from itinerary.views import views
from rest_framework.routers import DefaultRouter

#Use this for the api
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'trips', views.TripViewSet)
router.register(r'days', views.DayViewSet)
router.register(r'items', views.ItemViewSet)

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^create/', views.createTrip, name='create'),
	url(r'^allTrips/', views.showAllTrips, name='allTrips'),
	url(r'^trip/(?P<tripID>\d+)', views.showTrip, name='showTrip'),
	url(r'^login/', views.login, name='login'),
	url(r'^myTrips/', views.viewMyTrips, name='myTrips'),
	url(r'^getFriends/', views.getFriends, name='getFriends'),
	url(r'^shareWithFriends/', views.shareWithFriends, name='shareWithFriends'),
	url(r'^pastTrips/', views.viewPastTrips, name='pastTrips'),
	url(r'^updateItemPositions', views.updateItemPositions, name='updateItemPositions'),
	url(r'^yelpTest/', views.yelpTest, name='yelpTest'),
	url(r'^getFoursquareResults?', views.getFoursquareResults, name='getFoursquareResults'),
        url(r'^admin/', admin.site.urls),
	url(r'^api/', include(router.urls)),
]
