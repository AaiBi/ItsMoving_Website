from django.urls import path
from administration import views


urlpatterns = [
    path('admin_page/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),

    #Devis
    path('devis_home/', views.devis_home, name='devis_home'),
    path('devis_detail/<int:quote_request_pk>', views.devis_detail, name='devis_detail'),
    path('devis_detail/<int:quote_request_pk>', views.devis_detail, name='devis_detail'),
    path('delete_devis/<int:quote_request_pk>', views.delete_devis, name='delete_devis'),

    #Movers
    path('Movers/', views.movers_home, name='movers_home'),
    path('mover_detail/<int:mover_pk>', views.mover_detail, name='mover_detail'),
    path('mover_devis/<int:mover_pk>', views.mover_devis, name='mover_devis'),
    path('mover_active_unactive/<int:mover_pk>', views.mover_active_unactive, name='mover_active_unactive'),

    #Facturation
    path('Facturation/', views.facturation_home, name='facturation_home'),
    path('list_payments_not_done/<int:mover_pk>', views.list_payments_not_done, name='list_payments_not_done'),
    path('list_payments_done/<int:mover_pk>', views.list_payments_done, name='list_payments_done'),
    path('group_email_for_paiement/', views.group_email_for_paiement, name='group_email_for_paiement'),
]
