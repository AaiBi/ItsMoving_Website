from django.urls import path
from user import views


urlpatterns = [
    # Auth
    path('login/', views.login_user, name='login_user'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_user, name='logout_user'),
    path('reviews/', views.reviews, name='reviews'),
    path('preview/', views.preview, name='preview'),
    path('statistic/', views.statistic, name='statistic'),
    path('quote_request/', views.quote_request, name='quote_request'),
    path('settings/', views.settings, name='settings'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('billing/', views.billing, name='billing'),
    path('password/', views.user_password_change, name='user_password_change'),

    # SETTINGS
    path('area_intervention/', views.area_intervention, name='area_intervention'),
    path('moving_type/', views.moving_type, name='moving_type'),
    path('customer_type/', views.customer_type, name='customer_type'),
    path('delete_mover_country/<int:mover_country_pk>/<int:mover_pk>', views.delete_mover_country, name='delete_mover_country'),
    path('delete_mover_region/<int:mover_region_pk>/<int:mover_pk>', views.delete_mover_region, name='delete_mover_region'),
    path('delete_mover_moving_type1/<int:moving_type_pk>/<int:mover_pk>', views.delete_mover_moving_type1, name='delete_mover_moving_type1'),
    path('delete_mover_moving_type2/<int:moving_type_pk>/<int:mover_pk>', views.delete_mover_moving_type2, name='delete_mover_moving_type2'),
    path('modify_country_departure/<int:mover_country_pk>/', views.modify_country_departure, name='modify_country_departure'),
    path('modify_country_arrival/<int:mover_country_pk>/', views.modify_country_arrival, name='modify_country_arrival'),
    path('quote_request_settings/', views.quote_request_settings, name='quote_request_settings'),
]