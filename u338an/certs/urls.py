from django.urls import path, include
from . import views


urlpatterns = [
    path('create_cert/', views.create_cert, name='create_cert'),
    path('create_cert_p12/', views.create_cert_p12, name='create_cert_p12'),
    path('content_dir/', views.content_dir, name='content_dir'),
    path('download/<str:file_name>', views.download, name='download'),
    path('', views.base, name='base'),
]