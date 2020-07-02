from django.contrib import admin
from django.urls import path, include
from . import views

from django.conf.urls.static import  static
from django.conf import settings


urlpatterns = [
    path('', views.index),
    path('signup/',views.signup),
    path('signup_submit/',views.signup_submit),
    path('login/',views.login),
    path('logging_in/',views.logging_in),
    #path('viewMap/',views.viewMap),
    #path('uploadImage/',views.uploadImage),
    path('location/',views.access_location),
    path('send_location/',views.user_location),
    path('fetch_all_locations/',views.fetch_all_locations),
    path('logout/',views.logout)
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)