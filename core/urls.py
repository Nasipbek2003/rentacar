from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('car/<int:pk>/', views.car_detail, name='car_detail'),
    path('car/<int:pk>/<slug:slug>/', views.car_detail, name='car_detail'),
    path('book/<int:pk>/', views.book_car, name='book_car'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('review/<int:car_pk>/', views.add_review, name='add_review'),
    path('toggle-favorite/<int:car_pk>/', views.toggle_favorite, name='toggle_favorite'),
    path('my-favorites/', views.my_favorites, name='my_favorites'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]
