from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('merge/', views.merge_pdfs, name='merge'),
]
