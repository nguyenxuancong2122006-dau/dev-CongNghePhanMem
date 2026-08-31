from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from decimal import Decimal

from .models import (
    Product,
    Category,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Review,
    Promotion,
)


# =========================================================
# TRANG CHỦ
# =========================================================

def home(request):

    products = Product.objects.filter(
        is_active=True
    ).select_related('category')

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
    }

    return render(
        request,
        'home/index.html',
        context
    )


# =========================================================
# CHI TIẾT SẢN PHẨM
# =========================================================

def product_detail(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    reviews = Review.objects.filter(
        product=product
    ).select_related('customer')

    context = {
        'product': product,
        'reviews': reviews,
    }

    return render(
        request,
        'home/product_detail.html',
        context
    )


# =========================================================
# ĐĂNG KÝ
# =========================================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        full_name = request.POST.get(
            'full_name',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip().lower()

        phone = request.POST.get(
            'phone',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        password2 = request.POST.get(
            'password2',
            ''
        )

        # Kiểm tra họ tên
        if not full_name:

            messages.error(
                request,
                'Vui lòng nhập họ và tên.'
            )

            return redirect('register')

        # Kiểm tra email
        if not email:

            messages.error(
                request,
                'Vui lòng nhập email.'
            )

            return redirect('register')

        # Kiểm tra số điện thoại
        if not phone:

            messages.error(
                request,
                'Vui lòng nhập số điện thoại.'
            )

            return redirect('register')

        # Kiểm tra mật khẩu
        if not password:

            messages.error(
                request,
                'Vui lòng nhập mật khẩu.'
            )

            return redirect('register')

        # Kiểm tra mật khẩu nhập lại
        if password != password2:

            messages.error(
                request,
                'Mật khẩu nhập lại không khớp.'
            )

            return redirect('register')

        # Kiểm tra email đã tồn tại
        if User.objects.filter(
            username=email
        ).exists():

            messages.error(
                request,
                'Email này đã được đăng ký.'
            )

            return redirect('register')

        # Tạo User
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        # Lưu họ tên
        name_parts = full_name.split(
            ' ',
            1
        )

        if len(name_parts) == 2:

            user.first_name = name_parts[0]
            user.last_name = name_parts[1]

        else:

            user.first_name = full_name

        user.save()

        # Tạo CustomerProfile
        from .models import CustomerProfile

        CustomerProfile.objects.create(
            user=user,
            phone=phone
        )

        # Thông báo
        messages.success(
            request,
            'Đăng ký tài khoản thành công! Hãy đăng nhập.'
        )

        return redirect('login')

    return render(
        request,
        'home/register.html'
    )


# =========================================================
# ĐĂNG NHẬP
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        email = request.POST.get(
            'email'
        )

        password = request.POST.get(
            'password'
        )

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:

            if not user.is_active:

                messages.error(
                    request,
                    'Tài khoản của bạn đã bị khóa.'
                )

                return redirect('login')

            login(
                request,
                user
            )

            return redirect('home')

        messages.error(
            request,
            'Email hoặc mật khẩu không đúng.'
        )

    return render(
        request,
        'home/login.html'
    )


# =========================================================
# ĐĂNG XUẤT
# =========================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        'Bạn đã đăng xuất.'
    )

    return redirect('home')


# =========================================================
# GIỎ HÀNG
# =========================================================

@login_required
def cart(request):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    items = cart.items.select_related(
        'product'
    )

    context = {
        'cart': cart,
        'items': items,
    }

    return render(
        request,
        'home/cart.html',
        context
    )


# =========================================================
# THÊM SẢN PHẨM VÀO GIỎ
# =========================================================

@login_required
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    if product.quantity <= 0:

        messages.error(
            request,
            'Sản phẩm đã hết hàng.'
        )

        return redirect('home')

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:

        if item.quantity < product.quantity:

            item.quantity += 1
            item.save()

        else:

            messages.warning(
                request,
                'Số lượng sản phẩm trong giỏ đã đạt giới hạn tồn kho.'
            )

            return redirect('cart')

    else:

        item.quantity = 1
        item.save()

    messages.success(
        request,
        f'Đã thêm "{product.name}" vào giỏ hàng.'
    )

    return redirect('cart')


# =========================================================
# TĂNG SỐ LƯỢNG
# =========================================================

@login_required
def increase_cart(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if item.quantity < item.product.quantity:

        item.quantity += 1
        item.save()

    else:

        messages.warning(
            request,
            'Không thể tăng thêm vì sản phẩm không đủ tồn kho.'
        )

    return redirect('cart')


# =========================================================
# GIẢM SỐ LƯỢNG
# =========================================================

@login_required
def decrease_cart(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if item.quantity > 1:

        item.quantity -= 1
        item.save()

    else:

        item.delete()

    return redirect('cart')


# =========================================================
# XÓA SẢN PHẨM KHỎI GIỎ
# =========================================================

@login_required
def remove_from_cart(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    item.delete()

    messages.success(
        request,
        'Đã xóa sản phẩm khỏi giỏ hàng.'
    )

    return redirect('cart')


# =========================================================
# THANH TOÁN
# =========================================================

@login_required
def checkout(request):

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    items = cart.items.select_related(
        'product'
    )

    # Giỏ hàng trống
    if not items.exists():

        messages.warning(
            request,
            'Giỏ hàng của bạn đang trống.'
        )

        return redirect('cart')

    # Kiểm tra tồn kho
    for item in items:

        if item.product.quantity < item.quantity:

            messages.error(
                request,
                f'Sản phẩm "{item.product.name}" không đủ số lượng trong kho.'
            )

            return redirect('cart')

    # Lấy thông tin khách hàng
    try:

        customer = request.user.profile

    except Exception:

        customer = None

    # Tính tổng tiền
    subtotal = sum(
        item.subtotal
        for item in items
    )

    discount = Decimal('0')

    # =====================================================
    # POST - ĐẶT HÀNG
    # =====================================================

    if request.method == 'POST':

        full_name = request.POST.get(
            'full_name',
            ''
        ).strip()

        phone = request.POST.get(
            'phone',
            ''
        ).strip()

        address = request.POST.get(
            'address',
            ''
        ).strip()

        payment_method = request.POST.get(
            'payment_method',
            Order.PAYMENT_COD
        )

        note = request.POST.get(
            'note',
            ''
        ).strip()

        promotion_code = request.POST.get(
            'promotion_code',
            ''
        ).strip().upper()

        # =================================================
        # KIỂM TRA THÔNG TIN
        # =================================================

        if not full_name:

            messages.error(
                request,
                'Vui lòng nhập họ tên người nhận.'
            )

            return redirect('checkout')

        if not phone:

            messages.error(
                request,
                'Vui lòng nhập số điện thoại.'
            )

            return redirect('checkout')

        if not address:

            messages.error(
                request,
                'Vui lòng nhập địa chỉ nhận hàng.'
            )

            return redirect('checkout')

        # Kiểm tra phương thức thanh toán
        if payment_method not in [
            Order.PAYMENT_COD,
            Order.PAYMENT_BANK
        ]:

            payment_method = Order.PAYMENT_COD

        # =================================================
        # XỬ LÝ MÃ GIẢM GIÁ
        # =================================================

        promotion = None

        if promotion_code:

            try:

                promotion = Promotion.objects.get(
                    code=promotion_code
                )

            except Promotion.DoesNotExist:

                messages.error(
                    request,
                    'Mã giảm giá không tồn tại.'
                )

                return redirect('checkout')

            # Kiểm tra mã còn hiệu lực
            if not promotion.is_valid:

                messages.error(
                    request,
                    'Mã giảm giá đã hết hạn hoặc không còn hiệu lực.'
                )

                return redirect('checkout')

            # Kiểm tra giá trị đơn tối thiểu
            if subtotal < promotion.min_order_value:

                messages.error(
                    request,
                    f'Đơn hàng phải đạt tối thiểu '
                    f'{promotion.min_order_value:,.0f}đ '
                    f'để sử dụng mã này.'
                )

                return redirect('checkout')

            # Giảm theo phần trăm
            if promotion.discount_type == Promotion.DISCOUNT_PERCENT:

                discount = (
                    subtotal
                    * promotion.discount_value
                    / Decimal('100')
                )

                if promotion.max_discount is not None:

                    discount = min(
                        discount,
                        promotion.max_discount
                    )

            # Giảm số tiền cố định
            elif promotion.discount_type == Promotion.DISCOUNT_FIXED:

                discount = promotion.discount_value

            # Không cho giảm quá tổng tiền
            discount = min(
                discount,
                subtotal
            )

        # =================================================
        # TỔNG THANH TOÁN
        # =================================================

        total = subtotal - discount

        # =================================================
        # TẠO ĐƠN HÀNG
        # =================================================

        try:

            with transaction.atomic():

                # Kiểm tra tồn kho lần cuối
                for item in items:

                    product = Product.objects.select_for_update().get(
                        id=item.product.id
                    )

                    if product.quantity < item.quantity:

                        raise ValueError(
                            f'Sản phẩm "{product.name}" '
                            f'không đủ số lượng trong kho.'
                        )

                # -----------------------------------------
                # Tạo Order
                # -----------------------------------------

                order = Order.objects.create(

                    customer=request.user,

                    full_name=full_name,

                    phone=phone,

                    address=address,

                    total=total,

                    promotion=promotion,

                    discount=discount,

                    payment_method=payment_method,

                    status=Order.STATUS_PENDING,

                    note=note
                )

                # -----------------------------------------
                # Tạo OrderItem + trừ kho
                # -----------------------------------------

                for item in items:

                    product = Product.objects.select_for_update().get(
                        id=item.product.id
                    )

                    OrderItem.objects.create(

                        order=order,

                        product=product,

                        quantity=item.quantity,

                        price=product.price
                    )

                    product.quantity -= item.quantity

                    product.save(
                        update_fields=[
                            'quantity'
                        ]
                    )

                # -----------------------------------------
                # Tăng số lần sử dụng mã
                # -----------------------------------------

                if promotion:

                    promotion.used_count = F(
                        'used_count'
                    ) + 1

                    promotion.save(
                        update_fields=[
                            'used_count'
                        ]
                    )

                    promotion.refresh_from_db()

                # -----------------------------------------
                # Xóa giỏ hàng
                # -----------------------------------------

                cart.items.all().delete()

        except ValueError as e:

            messages.error(
                request,
                str(e)
            )

            return redirect('cart')

        # =================================================
        # ĐẶT HÀNG THÀNH CÔNG
        # =================================================

        messages.success(
            request,
            f'Đặt hàng thành công! Mã đơn hàng: #{order.id}'
        )

        return redirect(
            'order_detail',
            order_id=order.id
        )

    # =====================================================
    # HIỂN THỊ CHECKOUT
    # =====================================================

    context = {

        'cart': cart,

        'items': items,

        'subtotal': subtotal,

        'discount': discount,

        'total': subtotal - discount,

        'customer': customer,

    }

    return render(
        request,
        'home/checkout.html',
        context
    )


# =========================================================
# THÔNG TIN CÁ NHÂN
# =========================================================

@login_required
def profile(request):

    customer = request.user.profile

    if request.method == 'POST':

        full_name = request.POST.get(
            'full_name'
        )

        email = request.POST.get(
            'email'
        )

        phone = request.POST.get(
            'phone'
        )

        address = request.POST.get(
            'address'
        )

        if full_name:

            name_parts = full_name.strip().split(
                ' ',
                1
            )

            if len(name_parts) == 2:

                request.user.first_name = name_parts[0]
                request.user.last_name = name_parts[1]

            else:

                request.user.first_name = full_name

        request.user.email = email
        request.user.save()

        customer.phone = phone
        customer.address = address
        customer.save()

        messages.success(
            request,
            'Cập nhật thông tin thành công.'
        )

        return redirect('profile')

    context = {
        'customer': customer,
    }

    return render(
        request,
        'home/profile.html',
        context
    )


# =========================================================
# LỊCH SỬ ĐƠN HÀNG
# =========================================================

@login_required
def orders(request):

    order_list = Order.objects.filter(
        customer=request.user
    ).prefetch_related(
        'items__product'
    )

    context = {
        'orders': order_list,
    }

    return render(
        request,
        'home/orders.html',
        context
    )


# =========================================================
# CHI TIẾT ĐƠN HÀNG
# =========================================================

@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    items = order.items.select_related(
        'product'
    )

    context = {
        'order': order,
        'items': items,
    }

    return render(
        request,
        'home/order_detail.html',
        context
    )


# =========================================================
# HỦY ĐƠN HÀNG
# =========================================================

@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    if order.status == Order.STATUS_PENDING:

        order.status = Order.STATUS_CANCELLED
        order.save()

        # Trả lại số lượng tồn kho
        for item in order.items.all():

            item.product.quantity += item.quantity

            item.product.save()

        messages.success(
            request,
            'Đã hủy đơn hàng.'
        )

    else:

        messages.error(
            request,
            'Đơn hàng này không thể hủy.'
        )

    return redirect('orders')
