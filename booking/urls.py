from django.urls import path
from . import views

urlpatterns = [
    path('',                         views.calendar_view,         name='calendar'),
    path('login/',                   views.login_view,            name='login'),
    path('logout/',                  views.logout_view,           name='logout'),
    path('auth/callback/',           views.oidc_callback,         name='oidc_callback'),
    path('buchen/',                  views.booking_create,        name='booking_create'),
    path('buchen/erfolg/<int:pk>/',  views.booking_success,       name='booking_success'),
    path('buchen/erfolg/<int:pk>/ics/', views.booking_ics,        name='booking_ics'),
    path('buchungen/',               views.booking_list,          name='booking_list'),
    path('buchungen/<int:pk>/',      views.booking_detail,        name='booking_detail'),
    path('api/events/',              views.api_events,            name='api_events'),
    path('api/verfuegbarkeit/',      views.api_check_availability, name='api_check_availability'),
    path('stornieren/<uuid:token>/', views.booking_cancel,        name='booking_cancel'),
    path('impressum/',               views.impressum,             name='impressum'),
    path('datenschutz/',             views.datenschutz,           name='datenschutz'),
]
