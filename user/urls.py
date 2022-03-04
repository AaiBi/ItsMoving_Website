from django.urls import path
from user import views


urlpatterns = [
    # Auth
    path('login/', views.login_user, name='login_user'),
    path('password_change/', views.password_change, name='password_change'),
    path('password_recovery/<str:email>', views.password_recovery, name='password_recovery'),
    path('password_edit/<str:email>/<str:code>', views.password_edit, name='password_edit'),
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
    path('customer_type/', views.customer_type, name='customer_type'),
    path('delete_mover_country/<int:mover_country_pk>/<int:mover_pk>', views.delete_mover_country, name='delete_mover_country'),
    path('delete_mover_moving_type1/<int:moving_type_pk>/<int:mover_pk>', views.delete_mover_moving_type1, name='delete_mover_moving_type1'),
    path('delete_mover_moving_type2/<int:moving_type_pk>/<int:mover_pk>', views.delete_mover_moving_type2, name='delete_mover_moving_type2'),
    path('quote_request_settings/', views.quote_request_settings, name='quote_request_settings'),

    # QUOTE REQUEST
    path('mover_quote_request_detail/<int:mover_request_pk>', views.mover_quote_request_detail, name='mover_quote_request_detail'),
    path('mover_request_treated/<int:mover_request_pk>', views.mover_request_treated, name='mover_request_treated'),
    path('mover_request_rejected/<int:mover_request_pk>', views.mover_request_rejected, name='mover_request_rejected'),
    path('treated_quote_request/', views.treated_quote_request, name='treated_quote_request'),

    # REVIEWS
    path('reviews/<int:mover_request_pk>', views.review_request, name='review_request'),
]