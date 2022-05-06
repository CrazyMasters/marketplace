from rest_framework.routers import DefaultRouter

from .views import StoreViewSet
from .views import StoreContactViewSet
from .views import CategoryViewSet
from .views import ProductViewSet
from .views import ProductPhotoViewSet
from .views import ProductPropertyViewSet
from .views import CartPositionViewSet
from .views import CityViewSet
from .views import OrderAddressViewSet
from .views import OrderViewSet
from .views import OrderPositionViewSet

router = DefaultRouter()

router.register('stores', StoreViewSet)
router.register('store_contacts', StoreContactViewSet)
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)
router.register('products_protos', ProductPhotoViewSet)
router.register('products_properties', ProductPropertyViewSet)
router.register('cart', CartPositionViewSet)
router.register('cities', CityViewSet)
router.register('order_addresses', OrderAddressViewSet)
router.register('orders', OrderViewSet)
router.register('orders_positions', OrderPositionViewSet)

urlpatterns = router.urls
