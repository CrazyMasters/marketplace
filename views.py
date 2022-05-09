from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.utils import json, encoders

from django.db.models import Sum, F
from django.db import transaction
from django.conf import settings

from .models import Store
from .models import StoreContact
from .models import Category
from .models import Product
from .models import ProductPhoto
from .models import ProductProperty
from .models import CartPosition
from .models import City
from .models import OrderAddress
from .models import Order
from .models import OrderPosition

from .serializers import StoreSerializer
from .serializers import StoreContactSerializer
from .serializers import CategorySerializer
from .serializers import ProductSerializer
from .serializers import ProductPhotoSerializer
from .serializers import ProductPropertySerializer
from .serializers import CartPositionSerializer
from .serializers import CitySerializer
from .serializers import OrderAddressSerializer
from .serializers import OrderSerializer
from .serializers import OrderPositionSerializer
from .serializers import ProductAdminSerializer
from .serializers import StoreAdminSerializer

from .pagination import StandardPagination

from .filters import query_params_filter

from yookassa import Configuration, Payment, Refund

from pyfcm import FCMNotification

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()
push_service = FCMNotification(api_key=settings.FCM_DJANGO_SETTINGS["FCM_SERVER_KEY"])

Configuration.account_id = settings.YOOKASSA_MARKETPLACE["account_id"]
Configuration.secret_key = settings.YOOKASSA_MARKETPLACE["secret_key"]


class StoreViewSet(ReadOnlyModelViewSet):
    queryset = Store.objects.filter(moderator_confirmed=True, blocked=False)
    serializer_class = StoreSerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['city']
    filter_char_fields = ['name']
    search_fields = ['name', 'city__name', 'description']
    ordering_fields = ['name', 'city']

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(StoreViewSet, self).filter_queryset(queryset)


class StoreContactViewSet(ReadOnlyModelViewSet):
    queryset = StoreContact.objects.filter(store__moderator_confirmed=True, store__blocked=False)
    serializer_class = StoreContactSerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['store']
    filter_char_fields = ['contact_name', 'contact_data']
    search_fields = ['contact_name', 'contact_data', 'description']
    ordering_fields = ['contact_name', 'contact_data', 'description']

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(StoreContactViewSet, self).filter_queryset(queryset)


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.filter(moderator_confirmed=True)
    serializer_class = CategorySerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['category']
    filter_char_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'description']

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(CategoryViewSet, self).filter_queryset(queryset)


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.filter(category__moderator_confirmed=True, store__moderator_confirmed=True,
                                      store__blocked=False)
    serializer_class = ProductSerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['category', 'store']
    filter_char_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'description', 'cost']

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(ProductViewSet, self).filter_queryset(queryset)


class ProductPhotoViewSet(ReadOnlyModelViewSet):
    queryset = ProductPhoto.objects.filter(product__category__moderator_confirmed=True,
                                           product__store__moderator_confirmed=True, product__store__blocked=False)
    serializer_class = ProductPhotoSerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['product']
    filter_char_fields = []
    search_fields = []
    ordering_fields = []

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(ProductPhotoViewSet, self).filter_queryset(queryset)


class ProductPropertyViewSet(ReadOnlyModelViewSet):
    queryset = ProductProperty.objects.filter(product__category__moderator_confirmed=True,
                                              product__store__moderator_confirmed=True, product__store__blocked=False)
    serializer_class = ProductPropertySerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['product']
    filter_char_fields = []
    search_fields = []
    ordering_fields = []

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(ProductPropertyViewSet, self).filter_queryset(queryset)


class CartPositionViewSet(ReadOnlyModelViewSet):
    queryset = CartPosition.objects.all()
    serializer_class = CartPositionSerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['product', 'product__shop']
    filter_char_fields = []
    search_fields = ['product__name']
    ordering_fields = []

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
        if self.request.query_params.get('tmp'):
            return self.queryset.filter(tmp_user_code=self.request.query_params.get('tmp'))
        return self.queryset.none()

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(CartPositionViewSet, self).filter_queryset(queryset)

    @action(methods=["post"], detail=False)
    def sync(self, request):
        if request.user.is_authenticated:
            CartPosition.objects.filter(tmp_user_code=request.data.get("tmp")).update(user=request.user)
            return Response({"detail": "Synchronized successfully"}, status=200)
        return Response({"detail": "Unauthorized user"}, status=403)

    @action(methods=["post"], detail=False)
    def change(self, request):
        product_id = request.data.get("product")
        count = request.data.get("count")

        if not Product.objects.filter(id=product_id).exists():
            return Response({"detail": "Товар не существует"}, status=400)

        if self.get_queryset().filter(product_id=product_id).exists():
            if count >= 0:
                self.get_queryset().filter(product_id=product_id).update(count=count)
                return Response({'detail': 'зиция корзины успешно изменена'})
            else:
                self.get_queryset().filter(product_id=product_id).delete()
                return Response({'detail': 'Товар успешно удален из корзины'})
        else:
            if count <= 0:
                return Response({"detail": 'Невозможно добавить 0 и меньше товаров в корзину'}, status=400)
            elif not self.request.query_params.get("tmp"):
                return Response({"detail": "Укажите временный токен пользователя"}, status=400)
            else:
                self.queryset.create(product_id=product_id, count=count)
                return Response({'detail': 'Товар успешно добавлен в корзину'})

    @action(methods=["get"], detail=False)
    def amount(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        amount = queryset.aggregate(amount=Sum(F('product__cost') * F('count')))['amount']
        return Response({'amount': round(amount, 2)})

    @action(methods=['get'], detail=False)
    def is_many_stores(self, request):
        return Response({'many': self.get_queryset().values('product__shop').distinct().count() > 1})

    @action(methods=['get'], detail=False)
    def by_stores(self, request):
        resp = list()
        queryset = self.filter_queryset(self.get_queryset())
        store_names = queryset.values_list('product__store__name', flat=True).distinct()
        store_id_list = queryset.values_list('product__store_id', flat=True).distinct()
        for name, identifier in zip(store_names, store_id_list):
            positions = queryset.filter(product__shop__name=name)
            amount = positions.aggregate(amount=Sum(F('product__cost') * F('count')))['amount']
            resp.append({
                'store_name': name,
                'store_id': identifier,
                'cart_positions': self.get_serializer(positions, many=True).data,
                'amount': round(amount, 2)
            })
        return Response(resp)


class CityViewSet(ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = []
    filter_char_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(CityViewSet, self).filter_queryset(queryset)


class OrderAddressViewSet(ModelViewSet):
    queryset = OrderAddress.objects.all()
    serializer_class = OrderAddressSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = []
    filter_char_fields = ['address']
    search_fields = ['address']
    ordering_fields = ['address']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(OrderAddressViewSet, self).filter_queryset(queryset)


class OrderViewSet(ReadOnlyModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['address', 'paid', 'completed', 'delivered']
    filter_char_fields = []
    search_fields = ['address__address']
    ordering_fields = ['amount']
    actions_permission_classes = {
        'default': [AllowAny],
        'create': [IsAuthenticated],
        'pay': [IsAuthenticated],
        'pay_notifications': [AllowAny],
    }

    def get_permissions(self):
        if self.action in self.actions_permission_classes:
            return [permission() for permission in self.actions_permission_classes[self.action]]
        return [permission() for permission in self.actions_permission_classes['default']]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(OrderViewSet, self).filter_queryset(queryset)

    @transaction.atomic
    @action(methods=['post'], detail=False)
    def create(self, request):
        store_id = request.data.get('store')
        address_id = request.data.get('address')

        if not isinstance(store_id, int):
            return Response({'detail': 'Идентификатор магазина должен представлять целое число'}, status=400)
        if not isinstance(address_id, int):
            return Response({'detail': 'Идентификатор адреса должен представлять целое число'}, status=400)
        if not request.user.cartposition_set.filter(product__store_id=store_id).count():
            return Response({'detail': 'В вашей корзине нет товаров из этого магазина'}, status=400)
        if not request.user.orderaddress_set.filter(id=address_id).exists():
            return Response({'detail': 'Неверный идентификатор адреса'}, status=400)

        cart_positions = request.user.cartposition_set.filter(product__store_id=store_id)
        amount = round(cart_positions.aggregate(amount=Sum(F('product__cost') * F('count')))['amount'], 2)
        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": 'RUB'
            },
            "confirmation": {
                "type": "redirect",
                "return_url": settings.YOOKASSA_MARKETPLACE["confirmation_redirect_url"]
            },
            "capture": True,
            "description": f"Заказ USER:{request.user.id} {str(amount)}RUB"
        })
        order = Order.objects.create(
            store_id=store_id, address_id=address_id, user=request.user, amount=amount, payment_id=payment.id
        )
        for cart_position in cart_positions:
            order.orderposition_set.create(product=cart_position.product, count=cart_position.count)
        serializer = self.get_serializer(order)
        order_data = serializer.data
        order_text_data = json.dumps(order_data, cls=encoders.JSONEncoder, ensure_ascii=False)
        async_to_sync(channel_layer.group_send)(
            f"order-admin-{order.store.user_id}", {"type": "new_order", "message": order_text_data}
        )
        return Response(order_data, status=201)

    @transaction.atomic
    @action(methods=['post'], detail=True)
    def pay(self, request, pk):
        instance = self.get_object()
        if instance.canceled:
            return Response({'detail': 'Заказ был отменен'}, status=400)
        if instance.payment_id:
            payment = Payment.find_one(instance.payment_id)
        else:
            payment = Payment.create({
                "amount": {
                    "value": str(instance.amount),
                    "currency": 'RUB'
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": settings.YOOKASSA_MARKETPLACE["confirmation_redirect_url"]
                },
                "capture": True,
                "description": f"Заказ USER:{instance.user_id} {str(instance.amount)}RUB"
            })
            instance.payment_id = payment.id
            instance.save()
        return Response(payment.json())

    @action(methods=['post'], detail=False)
    def pay_notifications(self, request):
        payment = request.data.get("object")
        instance = Order.objects.get(payment_id=payment['id'])
        if payment["status"] == "succeeded":
            instance.paid = True
            instance.save()
            instance_data = self.get_serializer(instance).data
            instance_text_data = json.dumps(instance_data, cls=encoders.JSONEncoder, ensure_ascii=False)
            async_to_sync(channel_layer.group_send)(
                f"order-{instance.id}", {"type": "order_change", "message": instance_text_data}
            )
            async_to_sync(channel_layer.group_send)(
                f"order-admin-{instance.id}", {"type": "order_paid", "message": instance_text_data}
            )
            extra_notification_kwargs = {
                "push_type": "order_change",
                "order_id": instance.id,
                "order": instance_data
            }
            push_service.notify_topic_subscribers(
                message_title=f"Заказ #{instance.id} оплачен",
                badge=1,
                topic_name=str(instance.user_id),
                message_body="Заказ успешно оплачен! Продавец уже начал его собирать.",
                sound="default",
                extra_notification_kwargs=extra_notification_kwargs
            )
        else:
            payment = Payment.create({
                "amount": {
                    "value": str(instance.amount),
                    "currency": 'RUB'
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": settings.YOOKASSA_MARKETPLACE["confirmation_redirect_url"]
                },
                "capture": True,
                "description": f"Заказ USER:{instance.user_id} {str(instance.amount)}RUB"
            })
            instance.payment_id = payment.id
            instance.save()
        return Response(status=200)


class OrderPositionViewSet(ReadOnlyModelViewSet):
    queryset = OrderPosition.objects.all()
    serializer_class = OrderPositionSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['order', 'product']
    filter_char_fields = ['product__name']
    search_fields = ['product__name']
    ordering_fields = ['count']

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(OrderPositionViewSet, self).filter_queryset(queryset)


class OrderAdminViewSet(GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['store', 'user', 'paid', 'completed', 'delivered']
    filter_char_fields = ['store__name']
    search_fields = ['store__name']
    ordering_fields = ['store__name']

    def get_queryset(self):
        return self.queryset.filter(store__user=self.request.user)

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(OrderAdminViewSet, self).filter_queryset(queryset)

    @transaction.atomic
    @action(methods=['post'], detail=True)
    def cancel(self, request, pk):
        instance = self.get_object()
        if instance.canceled:
            return Response({'detail': 'Заказ уже был отменен'}, status=400)
        if instance.paid:
            Refund.create({
                "amount": {
                    "value": str(instance.amount),
                    "currency": "RUB"
                },
                "payment_id": instance.payment_id
            })
        instance.canceled = True
        instance.save()
        return Response({'detail': 'Заказ успешно отменен'}, status=200)


class OrderPositionAdminViewSet(ModelViewSet):
    queryset = OrderPosition.objects.all()
    serializer_class = OrderPositionSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['order', 'product']
    filter_char_fields = ['product__name']
    search_fields = ['product__name']
    ordering_fields = ['count']

    def get_queryset(self):
        return self.queryset.filter(order__store__user=self.request.user)

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(OrderPositionAdminViewSet, self).filter_queryset(queryset)


class ProductAdminViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductAdminSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['category', 'store']
    filter_char_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'description', 'cost']

    def get_queryset(self):
        return self.queryset.filter(store__user=self.request.user)

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(ProductAdminViewSet, self).filter_queryset(queryset)


class ProductPhotoAdminViewSet(ModelViewSet):
    queryset = ProductPhoto.objects.all()
    serializer_class = ProductPhotoSerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['product']
    filter_char_fields = []
    search_fields = []
    ordering_fields = []

    def get_queryset(self):
        return self.queryset.filter(product__store__user=self.request.user)

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(ProductPhotoAdminViewSet, self).filter_queryset(queryset)


class ProductPropertyAdminViewSet(ModelViewSet):
    queryset = ProductProperty.objects.all()
    serializer_class = ProductPropertySerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['product']
    filter_char_fields = []
    search_fields = []
    ordering_fields = []

    def get_queryset(self):
        return self.queryset.filter(product__store__user=self.request.user)

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(ProductPropertyAdminViewSet, self).filter_queryset(queryset)


class StoreAdminViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreAdminSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['city']
    filter_char_fields = ['name']
    search_fields = ['name', 'city__name', 'description']
    ordering_fields = ['name', 'city']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(StoreAdminViewSet, self).filter_queryset(queryset)


class StoreContactAdminViewSet(ModelViewSet):
    queryset = StoreContact.objects.all()
    serializer_class = StoreContactSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filter_key_fields = ['store']
    filter_char_fields = ['contact_name', 'contact_data']
    search_fields = ['contact_name', 'contact_data', 'description']
    ordering_fields = ['contact_name', 'contact_data', 'description']

    def get_queryset(self):
        return self.queryset.filter(store__user=self.request.user)

    def filter_queryset(self, queryset):
        queryset = query_params_filter(self.request, queryset, self.filter_key_fields, self.filter_char_fields)
        return super(StoreContactAdminViewSet, self).filter_queryset(queryset)
