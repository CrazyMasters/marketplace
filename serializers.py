from rest_framework import serializers

from .models import Store
from .models import StoreContact
from .models import Category
from .models import Product
from .models import ProductGroup
from .models import ProductPhoto
from .models import ProductProperty
from .models import CartPosition
from .models import City
from .models import OrderAddress
from .models import Order
from .models import OrderPosition
from .models import Discount
from .models import Bundle
from .models import BundlePosition
from .models import BundlePhoto
from .models import DeliveryCost


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'logo', 'city', 'description']


class StoreContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreContact
        fields = ['id', 'store', 'contact_name', 'contact_data', 'description']


class CategorySerializer(serializers.ModelSerializer):
    nested = serializers.BooleanField(read_only=True)

    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    _category = CategorySerializer(read_only=True)
    _store = StoreSerializer(read_only=True)
    cost = serializers.FloatField(read_only=True)
    photos = serializers.SerializerMethodField()
    cost_with_discount = serializers.SerializerMethodField()

    def get_cost_with_discount(self, instance):
        return instance.dynamic_cost()

    def get_photos(self, instance):
        return [
            f"{self.context['request'].META['wsgi.url_scheme']}://{self.context['request'].META['HTTP_HOST']}{i.img.url}"
            for i in instance.productphoto_set.all()
        ]

    class Meta:
        model = Product
        fields = '__all__'


class ProductGroupSerializer(serializers.ModelSerializer):
    _store = StoreSerializer(read_only=True, source='store')

    class Meta:
        model = ProductGroup
        fields = '__all__'


class ProductPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhoto
        fields = '__all__'


class ProductPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductProperty
        fields = '__all__'


class CartPositionSerializer(serializers.ModelSerializer):
    _product = ProductSerializer(read_only=True)
    cost = serializers.SerializerMethodField()
    cost_with_discount = serializers.SerializerMethodField()

    def get_cost_with_discount(self, instance):
        return instance.product.dynamic_cost()

    def get_cost(self, instance):
        return round(instance.product.cost * instance.count, 2)

    class Meta:
        model = CartPosition
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    longitude = serializers.FloatField(read_only=True)
    latitude = serializers.FloatField(read_only=True)

    class Meta:
        model = City
        fields = '__all__'


class OrderAddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    _city = serializers.SlugRelatedField(read_only=True, slug_field='name', source='city')

    class Meta:
        model = OrderAddress
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    _address = serializers.SlugRelatedField(read_only=True, slug_field='address', source='address')
    _store = StoreSerializer(read_only=True)
    status = serializers.CharField(read_only=True)
    amount = serializers.FloatField()
    created_time = serializers.DateTimeField(format='%d.%m.%Y %H:%M', read_only=True)
    canceled = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'store', '_store', 'user', 'address', '_address', 'amount', 'created_time', 'paid', 'completed',
            'delivered', 'canceled', 'status'
        ]


class OrderAdminSerializer(serializers.ModelSerializer):
    address = serializers.SlugRelatedField(read_only=True, slug_field='address')
    status = serializers.CharField(read_only=True)
    amount = serializers.FloatField(read_only=True)
    created_time = serializers.DateTimeField(format='%d.%m.%Y %H:%M', read_only=True)
    paid = serializers.BooleanField(read_only=True)
    canceled = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'store', 'user', 'address', 'amount', 'created_time', 'paid', 'completed', 'delivered', 'canceled',
            'status'
        ]


class OrderPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPosition
        fields = '__all__'


class ProductAdminSerializer(serializers.ModelSerializer):
    _category = CategorySerializer(read_only=True)
    _store = StoreSerializer(read_only=True)
    cost = serializers.FloatField()
    photos = serializers.SerializerMethodField()
    moderator_confirmed = serializers.SlugRelatedField(read_only=True, slug_field='moderator_confirmed',
                                                       source='category')
    blocked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class StoreAdminSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    moderator_confirmed = serializers.BooleanField(read_only=True)
    blocked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Store
        fields = '__all__'


class DiscountSerializer(serializers.ModelSerializer):

    _product = serializers.SlugRelatedField(read_only=True, slug_field="name", source="product")

    class Meta:
        model = Discount
        fields = "__all__"


class BundleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bundle
        fields = "__all__"


class BundlePositionSerializer(serializers.ModelSerializer):

    _product = serializers.SlugRelatedField(read_only=True, slug_field="name", source="product")

    class Meta:
        model = BundlePosition
        fields = "__all__"


class DeliveryCostSerializer(serializers.ModelSerializer):

    _store = serializers.SlugRelatedField(read_only=True, slug_field="name", source="store")
    _city = serializers.SlugRelatedField(read_only=True, slug_field="name", source="city")

    class Meta:
        model = DeliveryCost
        fields = "__all__"


class BundlePhotoSerializer(serializers.ModelSerializer):

    _bundle = serializers.SlugRelatedField(read_only=True, slug_field="title", source="bundle")

    class Meta:
        model = BundlePhoto
        fields = "__all__"

