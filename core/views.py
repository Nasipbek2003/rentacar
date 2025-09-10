from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Car, Order, Review, Favorite, CarCategory, UserProfile
from .forms import BookingForm, ReviewForm, UserRegistrationForm, UserProfileForm, CarSearchForm


def home(request):
    # Получаем параметры поиска
    form = CarSearchForm(request.GET)
    cars = Car.objects.filter(available=True)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        brand = form.cleaned_data.get('brand')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        fuel_type = form.cleaned_data.get('fuel_type')
        transmission = form.cleaned_data.get('transmission')
        seats = form.cleaned_data.get('seats')
        
        if search:
            cars = cars.filter(
                Q(name__icontains=search) |
                Q(brand__icontains=search) |
                Q(model__icontains=search) |
                Q(description__icontains=search)
            )
        
        if brand:
            cars = cars.filter(brand__icontains=brand)
        
        if min_price:
            cars = cars.filter(price_per_day__gte=min_price)
        
        if max_price:
            cars = cars.filter(price_per_day__lte=max_price)
        
        if fuel_type:
            cars = cars.filter(fuel_type=fuel_type)
        
        if transmission:
            cars = cars.filter(transmission=transmission)
        
        if seats:
            cars = cars.filter(seats__gte=seats)
    
    # Сортировка
    sort_by = request.GET.get('sort', 'created_at')
    if sort_by == 'price_asc':
        cars = cars.order_by('price_per_day')
    elif sort_by == 'price_desc':
        cars = cars.order_by('-price_per_day')
    elif sort_by == 'rating':
        cars = cars.order_by('-rating')
    elif sort_by == 'year':
        cars = cars.order_by('-year')
    else:
        cars = cars.order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(cars, 12)  # 12 автомобилей на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Статистика для главной страницы
    total_cars = Car.objects.filter(available=True).count()
    categories = CarCategory.objects.all()
    featured_cars = Car.objects.filter(available=True, rating__gte=4.0)[:3]
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_cars': total_cars,
        'categories': categories,
        'featured_cars': featured_cars,
        'current_sort': sort_by,
    }
    return render(request, 'core/home.html', context)


def car_detail(request, pk, slug=None):
    car = get_object_or_404(Car, pk=pk)
    reviews = car.car_reviews.all()[:5]  # Последние 5 отзывов
    
    # Проверяем, добавлен ли автомобиль в избранное
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, car=car).exists()
    
    # Похожие автомобили
    similar_cars = Car.objects.filter(
        brand=car.brand, available=True
    ).exclude(pk=car.pk)[:4]
    
    context = {
        'car': car,
        'reviews': reviews,
        'is_favorite': is_favorite,
        'similar_cars': similar_cars,
    }
    return render(request, 'core/car_detail.html', context)


@login_required
def book_car(request, pk):
    car = get_object_or_404(Car, pk=pk, available=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.car = car
            
            # Вычисляем общую стоимость
            duration = (order.end_date - order.start_date).days + 1
            total_price = car.price_per_day * duration
            
            # Добавляем стоимость дополнительных услуг
            if order.child_seat:
                total_price += Decimal('500') * duration
            if order.additional_driver:
                total_price += Decimal('300') * duration
            if order.insurance:
                total_price += Decimal('800') * duration
            
            order.total_price = total_price
            order.save()
            
            messages.success(request, 'Ваш заказ успешно оформлен! Мы свяжемся с вами в ближайшее время.')
            return redirect('core:order_success', order_id=order.id)
    else:
        # Предзаполняем форму данными пользователя
        initial_data = {}
        if hasattr(request.user, 'userprofile'):
            profile = request.user.userprofile
            initial_data['phone'] = profile.phone
        initial_data['email'] = request.user.email
        
        form = BookingForm(initial=initial_data)
    
    context = {
        'car': car,
        'form': form,
    }
    return render(request, 'core/book_car.html', context)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'core/order_success.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/my_orders.html', {'page_obj': page_obj})


@login_required
def add_review(request, car_pk):
    car = get_object_or_404(Car, pk=car_pk)
    
    # Проверяем, арендовал ли пользователь этот автомобиль
    has_rented = Order.objects.filter(
        user=request.user, 
        car=car, 
        status__in=['completed', 'active']
    ).exists()
    
    if not has_rented:
        messages.error(request, 'Вы можете оставить отзыв только на автомобили, которые арендовали.')
        return redirect('core:car_detail', pk=car.pk, slug=car.slug)
    
    # Проверяем, есть ли уже отзыв от этого пользователя
    existing_review = Review.objects.filter(user=request.user, car=car).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.car = car
            review.save()
            
            # Обновляем рейтинг автомобиля
            avg_rating = car.car_reviews.aggregate(Avg('rating'))['rating__avg']
            car.rating = round(avg_rating, 2) if avg_rating else 0
            car.reviews_count = car.car_reviews.count()
            car.save()
            
            messages.success(request, 'Ваш отзыв успешно добавлен!')
            return redirect('core:car_detail', pk=car.pk, slug=car.slug)
    else:
        form = ReviewForm(instance=existing_review)
    
    context = {
        'car': car,
        'form': form,
        'existing_review': existing_review,
    }
    return render(request, 'core/add_review.html', context)


@login_required
def toggle_favorite(request, car_pk):
    if request.method == 'POST':
        car = get_object_or_404(Car, pk=car_pk)
        favorite, created = Favorite.objects.get_or_create(user=request.user, car=car)
        
        if not created:
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True
        
        return JsonResponse({
            'is_favorite': is_favorite,
            'favorites_count': Favorite.objects.filter(car=car).count()
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('car')
    paginator = Paginator(favorites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/my_favorites.html', {'page_obj': page_obj})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль пользователя
            UserProfile.objects.create(user=user)
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    # Статистика пользователя
    orders_count = Order.objects.filter(user=request.user).count()
    favorites_count = Favorite.objects.filter(user=request.user).count()
    reviews_count = Review.objects.filter(user=request.user).count()
    
    context = {
        'form': form,
        'orders_count': orders_count,
        'favorites_count': favorites_count,
        'reviews_count': reviews_count,
    }
    return render(request, 'core/profile.html', context)
