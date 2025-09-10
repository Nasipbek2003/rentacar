from django.contrib import admin
from .models import Car, Order, CarCategory, Review, Favorite, UserProfile


@admin.register(CarCategory)
class CarCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'model', 'year', 'category', 'price_per_day', 'available', 'rating']
    list_filter = ['brand', 'year', 'available', 'category', 'fuel_type', 'transmission']
    search_fields = ['name', 'brand', 'model']
    prepopulated_fields = {'slug': ('brand', 'model', 'year')}
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'brand', 'model', 'year', 'category', 'slug', 'description')
        }),
        ('Цены', {
            'fields': ('price_per_day', 'price_per_hour')
        }),
        ('Изображения', {
            'fields': ('image', 'image2', 'image3')
        }),
        ('Технические характеристики', {
            'fields': ('fuel_type', 'transmission', 'seats', 'doors', 'engine_volume', 'power')
        }),
        ('Особенности', {
            'fields': ('air_conditioning', 'gps', 'bluetooth', 'parking_sensors', 'reverse_camera')
        }),
        ('Статус и рейтинг', {
            'fields': ('available', 'rating', 'reviews_count')
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'car', 'start_date', 'end_date', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at', 'start_date', 'end_date']
    search_fields = ['user__username', 'car__name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'car', 'start_date', 'end_date', 'status')
        }),
        ('Локации', {
            'fields': ('pickup_location', 'return_location')
        }),
        ('Дополнительные услуги', {
            'fields': ('child_seat', 'additional_driver', 'insurance')
        }),
        ('Контакты', {
            'fields': ('phone', 'email', 'notes')
        }),
        ('Финансы', {
            'fields': ('total_price',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'car', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'car__name', 'comment']
    readonly_fields = ['created_at']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'car', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'car__name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'driver_license', 'created_at']
    search_fields = ['user__username', 'phone', 'driver_license']
    readonly_fields = ['created_at']
