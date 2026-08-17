from django.urls import path
from . import views

app_name = 'pdf_tools'

urlpatterns = [
    path('merge/', views.MergeView.as_view(), name='merge'),
]
