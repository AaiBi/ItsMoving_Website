from django.urls import path
from administration import views


urlpatterns = [
    path('admin_page/', views.admin_login, name='admin_login'),
    path('home/', views.admin_home, name='admin_home'),
    path('logout/', views.admin_logout, name='admin_logout'),

    #Devis
    path('devis_home/', views.devis_home, name='devis_home'),
    path('devis_detail/<int:quote_request_pk>', views.devis_detail, name='devis_detail'),

    #Movers
    path('Movers/', views.movers_home, name='movers_home'),
    path('mover_detail/<int:mover_pk>', views.mover_detail, name='mover_detail'),
]
