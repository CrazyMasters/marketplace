from django.contrib import admin

from .models import Store
from .models import StoreContact
from .models import Category
from .models import Product
from .models import ProductPhoto
from .models import ProductProperty
from .models import City
from .models import Order
from .models import OrderPosition


class StoreContactInline(admin.TabularInline):
    model = StoreContact
    fk_name = "store"
    extra = 0


class StoreAdmin(admin.ModelAdmin):
    model = Store
    list_display = ("id", "user", "name", "city", "moderator_confirmed", "blocked", "description")
    list_filter = ("blocked", "moderator_confirmed", "city",)
    fieldsets = (
        (None, {
            'fields': (("user", "city",), ("name", "description",), "logo")
        }),
        ("Модерация", {
            'fields': ("blocked", "moderator_confirmed",)
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': (("user", "city",), ("name", "description",), "logo")
        }),
        ("Модерация", {
            'fields': ("blocked", "moderator_confirmed",)
        }),
    )
    search_fields = ("name", "description", "city__name")
    ordering = ("user", "name", "city", "moderator_confirmed", "blocked", "description")
    inlines = (StoreContactInline,)


class CategoryInline(admin.StackedInline):
    model = Category
    fk_name = "category"
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ('name', 'category', 'moderator_confirmed', 'description',)
    list_filter = ('moderator_confirmed',)
    firldsets = (
        (None, {
            'fields': ('name', 'category', 'img', 'description')
        }),
        ('Модерация', {
            'fields': ('moderator_confirmed',)
        })
    )
    add_fieldsets = (
        (None, {
            'fields': ('name', 'category', 'img', 'description')
        }),
        ('Модерация', {
            'fields': ('moderator_confirmed',)
        })
    )
    search_fields = ('name', 'category__name', 'description',)
    ordering = ('name', 'category', 'moderator_confirmed', 'description',)
    inlines = (CategoryInline,)


class ProductPhotoInline(admin.StackedInline):
    model = ProductPhoto
    fk_name = "product"
    extra = 0


class ProductPropertyInline(admin.TabularInline):
    model = ProductProperty
    fk_name = "product"
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'store', 'category', 'cost', 'count', 'blocked', 'description',)
    list_filter = ('blocked', 'category',)
    fieldsets = (
        (None, {
            'fields': ('name', 'store', 'category', 'cost', 'count', 'description',)
        }),
        ('Модерация', {
            'fields': ('blocked',)
        })
    )
    add_fieldsets = (
        (None, {
            'fields': ('name', 'store', 'category', 'cost', 'count', 'description',)
        }),
        ('Модерация', {
            'fields': ('blocked',)
        })
    )
    search_fields = ('name', 'store__name', 'category__name', 'description',)
    ordering = ('name', 'store', 'category', 'cost', 'count', 'blocked', 'description',)
    inlines = (ProductPhotoInline, ProductPropertyInline,)


class CityAdmin(admin.ModelAdmin):
    model = City
    list_display = ('name', 'longitude', 'latitude',)
    list_filter = ()
    fieldsets = (
        (None, {
            'fields': ('name', 'longitude', 'latitude',)
        })
    )
    add_fieldsets = (
        (None, {
            'fields': ('name', 'longitude', 'latitude',)
        })
    )
    search_fields = ('name',)
    ordering = ('name', 'longitude', 'latitude',)


class OrderPositionInline(admin.StackedInline):
    model = OrderPosition
    fk_name = "order"
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    def status(self, obj):
        s = obj.status
        if s == 'Ожидает оплаты':
            return f'<div style="width:100%%; height:100%%; background-color:gray;">{s}</div>'
        elif s == 'Собирается мгазином' or s == 'Доставляется':
            return f'<div style="width:100%%; height:100%%; background-color:blue;">{s}</div>'
        elif s == 'Доставлен':
            return f'<div style="width:100%%; height:100%%; background-color:green;">{s}</div>'
        elif s == 'Заказ отменен':
            return f'<div style="width:100%%; height:100%%; background-color:red;">{s}</div>'
        return s

    model = Order
    list_display = (
        'store', 'status', 'user', 'address', 'amount', 'paid', 'canceled', 'completed', 'delivered', 'created_time',
    )
    list_filter = ('paid', 'canceled', 'completed', 'delivered',)
    fieldsets = (
        (None, {
            'fields': (
                'store', 'user', 'address', 'amount',)
        }),
        ('Состояние', {
            'fields': ('paid', 'canceled', 'completed', 'delivered',)
        })
    )
    add_fieldsets = (
        (None, {
            'fields': (
                'store', 'user', 'address', 'amount',)
        }),
        ('Состояние', {
            'fields': ('paid', 'canceled', 'completed', 'delivered',)
        })
    )


admin.site.register(Store, StoreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Order, OrderAdmin)
