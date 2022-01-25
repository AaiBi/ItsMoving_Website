from django.urls import path
from base_app import views


urlpatterns = [
    path('mover_inscription/', views.mover_inscription, name='mover_inscription'),
    path('mover_inscription_step1/<int:mover_pk>', views.mover_inscription_step1, name='mover_inscription_step1'),
    path('mover_inscription_step2/<int:mover_pk>', views.mover_inscription_step2, name='mover_inscription_step2'),
    path('mover_inscription_step3/<int:mover_pk>', views.mover_inscription_step3, name='mover_inscription_step3'),
    path('mover_inscription_step4/<int:mover_pk>', views.mover_inscription_step4, name='mover_inscription_step4'),

    path('contact/', views.contact_page, name='contact_page'),
    path('devis_page1/', views.devis_page1, name='devis_page1'),
    path('international_moving/', views.article1_international_moving, name='article1_international_moving'),
    path('belgium_moving/', views.article2_belgium_moving, name='article2_belgium_moving'),
]
