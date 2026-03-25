from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.calendar_view,   name='calendar'),
    path('login/',              views.login_view,      name='login'),
    path('logout/',             views.logout_view,     name='logout'),
    path('buchen/',             views.booking_create,  name='booking_create'),
    path('buchen/erfolg/<int:pk>/', views.booking_success, name='booking_success'),
    path('buchungen/',          views.booking_list,    name='booking_list'),
    path('buchungen/<int:pk>/', views.booking_detail,  name='booking_detail'),
    path('api/events/',         views.api_events,      name='api_events'),
    path('impressum/',          views.impressum,       name='impressum'),
    path('datenschutz/',        views.datenschutz,     name='datenschutz'),
]
