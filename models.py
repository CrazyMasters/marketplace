import os
from decimal import Decimal
import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model


class Store(models.Model):
    def upload_store_logo(self, filename):
        return os.path.join("stores", str(self.id), filename)

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique=True)
    logo = models.ImageField(upload_to=upload_store_logo)
    city = models.ForeignKey("marketplace.City", on_delete=models.SET_NULL, null=True)
    moderator_confirmed = models.BooleanField(default=False)
    moderator_rejected = models.BooleanField(default=False)
    moderator_rejected_comment = models.TextField(blank=True)
    blocked = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    # legal info
    inn = models.CharField(max_length=100, blank=True)
    kpp = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    mail_index = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"


class StoreContact(models.Model):
    store = models.ForeignKey("marketplace.Store", on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=100)
    contact_data = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.contact_name}: {self.contact_data}'

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты магазинов"


class Category(models.Model):
    def upload_category_img(self, filename):
        return os.path.join("categories", str(self.id), filename)

    category = models.ForeignKey("marketplace.Category", on_delete=models.SET_NULL, default=None, null=True, blank=True,
                                 related_name='nested_categories')
    name = models.CharField(max_length=100, unique=True)
    img = models.ImageField(upload_to=upload_category_img, null=True, default=None)
    moderator_confirmed = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    @property
    def nested(self):
        return self.nested_categories.exists()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории товаров"


class Product(models.Model):
    name = models.CharField(max_length=1000)
    store = models.ForeignKey("marketplace.Store", on_delete=models.CASCADE)
    category = models.ForeignKey("marketplace.Category", on_delete=models.SET_NULL, null=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    code = models.CharField(max_length=150, default=None)
    group = models.ForeignKey('marketplace.ProductGroup', default=None, null=True, on_delete=models.SET_NULL)
    count = models.PositiveIntegerField()
    blocked = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True)

    def dynamic_cost(self):
        current_datetime = datetime.datetime.now()
        if self.discounts.all().exists():
            discount = self.discounts.filter(
                Q(date_start__lt=current_datetime) |
                Q(date_end__gt=current_datetime)).first()
            return self.cost - (self.cost / 100) * discount.discount_value
        else:
            return None

    # @property
    # def last_supply_date(self):
    #     if self.supply_set.filter(date__lte=timezone.now().date).exists():
    #         return self.supply_set.filter(date__lte=timezone.now().date).order_by("-date").first().date
    #     return None
    #
    # @property
    # def nearest_supply_date(self):
    #     if self.supply_set.filter(date__gt=timezone.now().date).exists():
    #         return self.supply_set.filter(date__gt=timezone.now().date).order_by("date").first().date
    #     return None

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        unique_together = ['code', 'store']


class ProductGroup(models.Model):
    store = models.ForeignKey('marketplace.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа товаров'
        verbose_name_plural = 'Группы товаров'


class ProductPhoto(models.Model):
    def upload_product_photo(self, filename):
        return os.path.join("products", str(self.product_id), filename)

    product = models.ForeignKey("marketplace.Product", on_delete=models.CASCADE)
    img = models.ImageField(upload_to=upload_product_photo)

    def __str__(self):
        return f'{self.product.name} ({self.id})'

    class Meta:
        verbose_name = 'Фотография товара'
        verbose_name_plural = 'Фотографии товаров'


class ProductProperty(models.Model):
    product = models.ForeignKey("marketplace.Product", on_delete=models.CASCADE)
    property_name = models.CharField(max_length=100)
    property_value = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.product.name}: {self.property_name} - {self.property_value}'

    class Meta:
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товаров'
        unique_together = ['product', 'property_name']


# class Supply(models.Model):
#     store = models.ForeignKey("marketplace.Product", on_delete=models.CASCADE)
#     date = models.DateField()
#
#     def __str__(self):
#         return f'{self.store.name} {self.date.strftime("%d.%m.%Y")}'
#
#     class Meta:
#         verbose_name = 'Привоз товаров'
#         verbose_name_plural = 'Привозы товаров'
#
#
# class SupplyPosition(models.Model):
#     supply = models.ForeignKey("marketplace.Supply", on_delete=models.CASCADE)
#     product = models.ForeignKey("marketplace.Product", on_delete=models.CASCADE)
#     count = models.PositiveIntegerField()
#
#     def __str__(self):
#         return f'{self.supply.store.name}: {self.product.name} ({self.supply.date.strftime("%d.%m.%Y")})'
#
#     class Meta:
#         verbose_name = 'Позиция привоза'
#         verbose_name_plural = 'Позиции привозов товаров'


class CartPosition(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, default=None)
    tmp_user_code = models.TextField(blank=True)
    product = models.ForeignKey("marketplace.Product", on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        # {self.user.name}:
        return f'{self.product.name} {self.count} шт.'

    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзин'


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    longitude = models.DecimalField(max_digits=23, decimal_places=17)
    latitude = models.DecimalField(max_digits=23, decimal_places=17)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class OrderAddress(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    address = models.TextField()
    longitude = models.DecimalField(max_digits=23, decimal_places=17)
    latitude = models.DecimalField(max_digits=23, decimal_places=17)

    def __str__(self):
        return f'{self.user.name}: {self.address}'

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса ппользователей'


class Order(models.Model):
    payment_id = models.CharField(max_length=100, default=None, null=True)
    store = models.ForeignKey('marketplace.Store', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey("marketplace.OrderAddress", on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_time = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    @property
    def status(self):
        if self.canceled:
            return 'Заказ отменен'
        if not self.paid:
            return 'Ожидает оплаты'
        if not self.completed:
            return 'Собирается мгазином'
        if not self.delivered:
            return 'Доставляется'
        return 'Доставлен'

    def __str__(self):
        return f'{self.user.name}: {self.amount} RUB ({self.status})'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderPosition(models.Model):
    order = models.ForeignKey('marketplace.Order', on_delete=models.CASCADE)
    product = models.ForeignKey('marketplace.Product', on_delete=models.SET_NULL, null=True)
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} {self.count} шт.'

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'


class Discount(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="discounts", default=None)
    product = models.ForeignKey("marketplace.Product", on_delete=models.CASCADE, related_name="discounts")
    discount_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(100)]
    )
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    def __str__(self):
        return f'Скидка на {self.product.name}'

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"


class Bundle(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="bundles", default=None)
    title = models.CharField(max_length=450)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal(0.01))]
    )
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Набор"
        verbose_name_plural = "Наборы"


class BundlePosition(models.Model):
    bundle = models.ForeignKey("marketplace.Bundle", on_delete=models.CASCADE, related_name="bundle_positions")
    product = models.ForeignKey("marketplace.Product", on_delete=models.CASCADE, related_name="bundle_positions")
    count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = "Позиция набора"
        verbose_name_plural = "Позиций набора"


class BundlePhoto(models.Model):
    def upload_bundle_photo(self, filename):
        return os.path.join("bundle", str(self.bundle_id), filename)

    bundle = models.ForeignKey("marketplace.Bundle", on_delete=models.CASCADE, related_name="photos")
    img = models.ImageField(upload_to=upload_bundle_photo)

    def __str__(self):
        return self.bundle.title

    class Meta:
        verbose_name = "Фотография набора"
        verbose_name_plural = "Фотографии наборов"


class DeliveryCost(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="delivery_costs", default=None)
    store = models.ForeignKey("marketplace.Store", on_delete=models.CASCADE, related_name="delivery_costs")
    city = models.ForeignKey("marketplace.City", on_delete=models.CASCADE, related_name="delivery_costs")
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal(0.0))]
    )
    discount_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal(0.0))]
    )
    cost_indication = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal(0.0))]
    )

    def __str__(self):
        return f'Цена доставки в {self.city.name}'

    class Meta:
        verbose_name = "Цена доставки"
        verbose_name_plural = "Цены доставки"

# test commit
# Another test
