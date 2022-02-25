from django.urls import path
from base_app import views


urlpatterns = [
    path('mover_inscription/', views.mover_inscription, name='mover_inscription'),
    path('mover_inscription_step1/<int:new_user_id>', views.mover_inscription_step1, name='mover_inscription_step1'),
    path('mover_inscription_step2/<int:new_user_id>/<int:mover_id>', views.mover_inscription_step2, name='mover_inscription_step2'),
    path('mover_inscription_step3/<int:new_user_id>/<int:mover_id>', views.mover_inscription_step3, name='mover_inscription_step3'),

    path('contact/', views.contact_page, name='contact_page'),
    path('international_moving/', views.article1_international_moving, name='article1_international_moving'),
    path('belgium_moving/', views.article2_belgium_moving, name='article2_belgium_moving'),

    #quote request
    path('devis_page1/', views.devis_page1, name='devis_page1'),
    path('devis_page2/<int:moving_type1_id>/<int:moving_type2_id>/<int:country_id>', views.devis_page2, name='devis_page2'),
    path('devis_page3/<int:moving_type1_id>/<int:moving_type2_id>/<int:country_id>/<str:City_Departure>/<str:Adresse_Departure>'
         '/<int:Postal_Code_Departure>/<str:Residence_Number_or_Name_Departure>/<str:Residence_Departure>/<int:Number_Room_Departure>',
         views.devis_page3, name='devis_page3'),
    path('devis_page4/<int:moving_type1_id>/<int:moving_type2_id>/<int:country_id>/<str:City_Departure>/<str:Adresse_Departure>'
         '/<int:Postal_Code_Departure>/<str:Residence_Number_or_Name_Departure>/<str:Residence_Departure>/<int:Number_Room_Departure>'
         '/<str:Country_Arrival>'
         '/<str:City_Arrival>/<str:Adresse_Arrival>/<int:Postal_Code_Arrival>/<str:Residence_Number_or_Name_Arrival>'
         '/<str:Residence_Arrival>', views.devis_page4, name='devis_page4'),
    path('devis_page5/<int:moving_type1_id>/<int:moving_type2_id>/<int:country_id>/<str:City_Departure>/<str:Adresse_Departure>'
         '/<int:Postal_Code_Departure>/<str:Residence_Number_or_Name_Departure>/<str:Residence_Departure>/<int:Number_Room_Departure>'
         '/<str:Country_Arrival>'
         '/<str:City_Arrival>/<str:Adresse_Arrival>/<int:Postal_Code_Arrival>/<str:Residence_Number_or_Name_Arrival>'
         '/<str:Residence_Arrival>/<str:firstname>/<str:lastname>/<str:email>/<str:phone_number>',
         views.devis_page5, name='devis_page5'),
    path('devis_page6', views.devis_page6, name='devis_page6'),
]
