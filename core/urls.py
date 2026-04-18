from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("plan/<str:plan_id>/", views.view_plan),
    path("capture-phone/", views.capture_phone),
    path("request-booking/", views.request_booking),
]