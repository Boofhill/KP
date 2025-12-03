from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .models import Employee, Filial, Position

class EmployeeCreationForm(UserCreationForm):
    # Поля из User (имя, фамилия, username, password, email)
    first_name = forms.CharField(max_length=30, required=True, label="Имя", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}))
    last_name = forms.CharField(max_length=30, required=True, label="Фамилия", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите фамилию'}))
    email = forms.EmailField(required=True, label="Email", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'}))

    # Поля из Employee
    filial = forms.ModelChoiceField(queryset=Filial.objects.all(), label="Филиал", widget=forms.Select(attrs={'class': 'form-control'}))
    position = forms.ModelChoiceField(queryset=Position.objects.all(), label="Должность", widget=forms.Select(attrs={'class': 'form-control'}))
    birth_date = forms.DateField(label="Дата рождения", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    internal_phone = forms.CharField(max_length=6, label="Внутренний телефон", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите 6 цифр'}))
    is_smus = forms.BooleanField(required=False, label="Является членом СМУС", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    photo = forms.ImageField(required=False, label="Фотография", widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите username'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean_internal_phone(self):
        phone = self.cleaned_data.get('internal_phone')
        if not re.match(r'^\d{6}$', phone):
            raise ValidationError("Внутренний телефон должен состоять из 6 цифр.")
        return phone

    def save(self, commit=True):
        # Сначала сохраняем User
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        # Затем Employee
        employee = Employee.objects.create(
            user=user,
            filial=self.cleaned_data['filial'],
            position=self.cleaned_data['position'],
            birth_date=self.cleaned_data['birth_date'],
            internal_phone=self.cleaned_data['internal_phone'],
            is_smus=self.cleaned_data['is_smus'],
            photo=self.cleaned_data.get('photo')
        )
        return employee

class EmployeeUpdateForm(forms.ModelForm):
    # Поля для обновления (User поля отдельно)
    first_name = forms.CharField(max_length=30, label="Имя", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}))  # Из User
    last_name = forms.CharField(max_length=30, label="Фамилия", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите фамилию'}))  # Из User

    class Meta:
        model = Employee
        fields = ['filial', 'position', 'photo', 'birth_date', 'internal_phone', 'is_smus']
        widgets = {
            'filial': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'internal_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите 6 цифр'}),
            'is_smus': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def clean_internal_phone(self):
        phone = self.cleaned_data.get('internal_phone')
        if not re.match(r'^\d{6}$', phone):
            raise ValidationError("Внутренний телефон должен состоять из 6 цифр.")
        return phone

    def save(self, commit=True):
        employee = super().save(commit=False)
        if commit:
            employee.user.first_name = self.cleaned_data['first_name']
            employee.user.last_name = self.cleaned_data['last_name']
            employee.user.save()
            employee.save()
        return employee

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Пароль должен быть не менее 8 символов.")
        return password