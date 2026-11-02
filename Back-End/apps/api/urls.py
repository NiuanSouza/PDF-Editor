from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Organização
    path('merge/', views.merge_pdfs, name='merge'),
    path('split/', views.split_pdf, name='split'),
    path('rotate/', views.rotate_pdf, name='rotate'),

    # Conversão Word <-> PDF
    path('word-to-pdf/', views.word_to_pdf, name='word_to_pdf'),
    path('pdf-to-word/', views.pdf_to_word, name='pdf_to_word'),

    # Conversão Imagens <-> PDF
    path('pdf-to-images/', views.pdf_to_images, name='pdf_to_images'),
    path('images-to-pdf/', views.images_to_pdf, name='images_to_pdf'),

    # Otimização e Segurança
    path('compress/', views.compress_pdf, name='compress'),
    path('protect/', views.protect_pdf, name='protect'),
    path('unlock/', views.unlock_pdf, name='unlock'),
    path('watermark/', views.watermark_pdf, name='watermark'),
]
