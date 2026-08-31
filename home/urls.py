from django.urls import path

from . import views


urlpatterns = [

    # =========================================================
    # TRANG CHỦ
    # =========================================================

    path(
        '',
        views.home,
        name='home'
    ),


    # =========================================================
    # SẢN PHẨM
    # =========================================================

    path(
        'san-pham/<int:product_id>/',
        views.product_detail,
        name='product_detail'
    ),


    # =========================================================
    # TÀI KHOẢN
    # =========================================================

    path(
        'dang-ky/',
        views.register_view,
        name='register'
    ),

    path(
        'dang-nhap/',
        views.login_view,
        name='login'
    ),

    path(
        'dang-xuat/',
        views.logout_view,
        name='logout'
    ),


    # =========================================================
    # GIỎ HÀNG
    # =========================================================

    path(
        'gio-hang/',
        views.cart,
        name='cart'
    ),

    path(
        'gio-hang/them/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        'gio-hang/tang/<int:item_id>/',
        views.increase_cart,
        name='increase_cart'
    ),

    path(
        'gio-hang/giam/<int:item_id>/',
        views.decrease_cart,
        name='decrease_cart'
    ),

    path(
        'gio-hang/xoa/<int:item_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    # Thanh toán
    path(
        'thanh-toan/',
        views.checkout,
        name='checkout'
    ),


    # =========================================================
    # CÁ NHÂN
    # =========================================================

    path(
        'tai-khoan/',
        views.profile,
        name='profile'
    ),


    # =========================================================
    # ĐƠN HÀNG
    # =========================================================

    path(
        'don-hang/',
        views.orders,
        name='orders'
    ),

    path(
        'don-hang/<int:order_id>/',
        views.order_detail,
        name='order_detail'
    ),

    path(
        'don-hang/<int:order_id>/huy/',
        views.cancel_order,
        name='cancel_order'
    ),
]
