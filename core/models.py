from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


class CarCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Car Categories"
    
    def __str__(self):
        return self.name


class Car(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Бензин'),
        ('diesel', 'Дизель'),
        ('electric', 'Электро'),
        ('hybrid', 'Гибрид'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('manual', 'Механическая'),
        ('automatic', 'Автоматическая'),
        ('cvt', 'Вариатор'),
    ]
    
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField(validators=[MinValueValidator(1990), MaxValueValidator(2030)])
    category = models.ForeignKey(CarCategory, on_delete=models.CASCADE, null=True, blank=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='cars/', blank=True, null=True)
    image2 = models.ImageField(upload_to='cars/', blank=True, null=True)
    image3 = models.ImageField(upload_to='cars/', blank=True, null=True)
    available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    
    # Технические характеристики
    fuel_type = models.CharField(max_length=10, choices=FUEL_CHOICES, default='petrol')
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES, default='manual')
    seats = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(9)])
    doors = models.IntegerField(default=4, validators=[MinValueValidator(2), MaxValueValidator(5)])
    engine_volume = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    power = models.IntegerField(null=True, blank=True, help_text="Мощность в л.с.")
    
    # Особенности
    air_conditioning = models.BooleanField(default=True)
    gps = models.BooleanField(default=False)
    bluetooth = models.BooleanField(default=False)
    parking_sensors = models.BooleanField(default=False)
    reverse_camera = models.BooleanField(default=False)
    
    # SEO
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    
    # Рейтинг
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, 
                                validators=[MinValueValidator(0), MaxValueValidator(5)])
    reviews_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"
    
    def get_absolute_url(self):
        return reverse('core:car_detail', kwargs={'pk': self.pk, 'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.brand}-{self.model}-{self.year}".lower().replace(' ', '-')
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('active', 'Активно'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    pickup_location = models.CharField(max_length=200)
    return_location = models.CharField(max_length=200)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Дополнительные услуги
    child_seat = models.BooleanField(default=False)
    additional_driver = models.BooleanField(default=False)
    insurance = models.BooleanField(default=False)
    
    # Контактная информация
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.car} для {self.user.username}"
    
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='car_reviews')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'car')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.car}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'car')
    
    def __str__(self):
        return f"{self.user.username} - {self.car}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    driver_license = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Профиль {self.user.username}"
