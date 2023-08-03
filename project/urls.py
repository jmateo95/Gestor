from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from horario.views import Index

urlpatterns = [
    path('admin/',          admin.site.urls),
    path('',                Index.as_view(),            name='index'),
    path('horario/',      include('horario.urls')),
]


def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)
handler403 = custom_403