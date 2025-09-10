from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, Review, UserProfile


class BookingForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'required': True
        }),
        label='Дата и время начала аренды'
    )
    
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'required': True
        }),
        label='Дата и время окончания аренды'
    )
    
    pickup_location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Адрес получения автомобиля'
        }),
        label='Место получения'
    )
    
    return_location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Адрес возврата автомобиля'
        }),
        label='Место возврата'
    )
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 123-45-67'
        }),
        label='Телефон'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com'
        }),
        label='Email'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Дополнительные пожелания или комментарии'
        }),
        label='Комментарии'
    )
    
    child_seat = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Детское кресло (+500 сом/день)'
    )
    
    additional_driver = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Дополнительный водитель (+300 сом/день)'
    )
    
    insurance = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Расширенная страховка (+800 сом/день)'
    )
    
    class Meta:
        model = Order
        fields = ['start_date', 'end_date', 'pickup_location', 'return_location', 
                 'phone', 'email', 'notes', 'child_seat', 'additional_driver', 'insurance']


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput(),
        label='Рейтинг'
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Поделитесь своим опытом аренды этого автомобиля...'
        }),
        label='Ваш отзыв'
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Фамилия'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Имя пользователя'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'date_of_birth', 'driver_license', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'driver_license': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер водительского удостоверения'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }


class CarSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по марке, модели или названию...'
        }),
        label='Поиск'
    )
    
    brand = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Марка автомобиля'
        }),
        label='Марка'
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'От'
        }),
        label='Цена от'
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'До'
        }),
        label='Цена до'
    )
    
    fuel_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Любой')] + [
            ('petrol', 'Бензин'),
            ('diesel', 'Дизель'),
            ('electric', 'Электро'),
            ('hybrid', 'Гибрид'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Тип топлива'
    )
    
    transmission = forms.ChoiceField(
        required=False,
        choices=[('', 'Любая')] + [
            ('manual', 'Механическая'),
            ('automatic', 'Автоматическая'),
            ('cvt', 'Вариатор'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Коробка передач'
    )
    
    seats = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=9,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Количество мест'
        }),
        label='Мест не менее'
    )

