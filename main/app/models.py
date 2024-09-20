from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.cache import cache
from social_django.models import UserSocialAuth



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        
        existing_user = self.model.objects.filter(email=email).first()
        if existing_user:

            for key, value in extra_fields.items():
                setattr(existing_user, key, value)
            existing_user.save(using=self._db)  
            return existing_user
        
        # Если пользователя нет, создаем нового
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, verbose_name='именем')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    def __str__(self) -> str:
        return self.email
    
    
# модель расходов
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('supermarkets', 'Супермаркеты'),
        ('Restaurants and cafes', 'Рестораны и кафе'),
        ('health and beauty', 'Здоровье и красота'),
        ('clothing and accessories', 'Одежда и аксессуары'),
        ('Utilities, communications, Internet', 'Коммунальные услуги, связь, интернет'),
        ('transport', 'Транспорт'),
        ('car', 'машина'),
        ('Education', 'Образование'),
        ('recreation and entertainment', 'Отдых и развлечения'),
        ('credit/mortgage', 'Кредит/Ипотека'),
        ('Everything for home', 'Товары для дома'),
        ('Other expenses', 'Прочие расходы'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='expenses', verbose_name='Пользователь',
                              on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name='Сумма (₽)')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Категория')
    title = models.CharField(max_length=40, verbose_name='Название')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Расход'
        verbose_name_plural = 'Расход'
        indexes = [
            models.Index(fields=['-date']),
        ]
        ordering = ['-date']

    def __str__(self) -> str:
        return f"{self.title} - {self.amount}₽"
    
    def get_category(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)
    
    def get_verbose_name(self):
        return self._meta.verbose_name
    

# модель доходов
class Income(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='incomes', verbose_name='Пользователь',
                              on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name='Сумма (₽)')
    title = models.CharField(max_length=40, verbose_name='Название')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Доход'
        verbose_name_plural = 'Доход'
        indexes = [
            models.Index(fields=['-date']),
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.amount}₽"
    
    def get_verbose_name(self):
        return self._meta.verbose_name
    
# модель цели накопления
class Goal(models.Model):
    STATUS_CHOICES = (
        ('current', 'Текущая'),
        ('completed', 'Завершённая'),
    )

    name = models.CharField(max_length=40, verbose_name='Название')
    target_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name='Цель (₽)')
    current_amount = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='current')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='goals',
                              verbose_name='пользователь',
                              on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'
        ordering = ['-status', '-date']
        
    def __str__(self) -> str:
        return self.name
    
    # проценты выполнения цели
    def percentage_to_target(self):
        if self.target_amount == 0:
            return 0  
        return round((self.current_amount / self.target_amount) * 100, 2)
    
    # изменение текущей суммы при добавлении, удалении, измении дохода
    def update_current_amount_on_income(self, amount):
        self.current_amount += amount
        if self.current_amount >= self.target_amount:
            self.current_amount = self.target_amount
            self.status = 'completed'
            cache.delete(f'goals_{self.user.id}')
        elif self.current_amount < 0:
            self.current_amount = 0
        self.save()

    # изменение текущей суммы при добавлении, удалении, измении расхода
    def update_current_amount_on_expense(self, amount):
        current_amount = self.current_amount - amount
        if current_amount >= self.target_amount:
            self.current_amount = self.target_amount
            self.status = 'completed'
            cache.delete(f'goals_{self.user.id}')
        elif current_amount < 0:
            self.current_amount = 0
        else:
            self.current_amount = current_amount
        self.save()
    
    def save(self, *args, **kwargs):
        if self.status == 'current':
            Goal.objects.filter(user=self.user, status='current') \
                        .exclude(pk=self.pk) \
                        .update(status='completed')
        super().save(*args, **kwargs)