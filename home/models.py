from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# =========================================================
# 1. THÔNG TIN KHÁCH HÀNG
# =========================================================

class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Số điện thoại'
    )

    address = models.TextField(
        blank=True,
        verbose_name='Địa chỉ'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = 'Thông tin khách hàng'
        verbose_name_plural = 'Thông tin khách hàng'


# =========================================================
# 2. DANH MỤC
# =========================================================

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Tên danh mục'
    )

    description = models.TextField(
        blank=True,
        verbose_name='Mô tả'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'


# =========================================================
# 3. SẢN PHẨM
# =========================================================

class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Danh mục'
    )

    name = models.CharField(
        max_length=200,
        verbose_name='Tên sản phẩm'
    )

    description = models.TextField(
        verbose_name='Mô tả'
    )

    price = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='Giá'
    )

    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Số lượng tồn kho'
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name='Hình ảnh'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Đang bán'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Ngày cập nhật'
    )

    def __str__(self):
        return self.name

    @property
    def is_out_of_stock(self):
        return self.quantity == 0

    @property
    def is_low_stock(self):
        return 0 < self.quantity <= 5

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'


# =========================================================
# 4. GIỎ HÀNG
# =========================================================

class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Khách hàng'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f'Giỏ hàng - {self.user.username}'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    class Meta:
        verbose_name = 'Giỏ hàng'
        verbose_name_plural = 'Giỏ hàng'


# =========================================================
# 5. CHI TIẾT GIỎ HÀNG
# =========================================================

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Giỏ hàng'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Sản phẩm'
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Số lượng'
    )

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='unique_cart_product'
            )
        ]
        verbose_name = 'Sản phẩm trong giỏ'
        verbose_name_plural = 'Sản phẩm trong giỏ'


# =========================================================
# 6. KHUYẾN MÃI
# =========================================================

class Promotion(models.Model):

    DISCOUNT_PERCENT = 'percent'
    DISCOUNT_FIXED = 'fixed'

    DISCOUNT_TYPE_CHOICES = [
        (DISCOUNT_PERCENT, 'Phần trăm'),
        (DISCOUNT_FIXED, 'Số tiền'),
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Mã giảm giá'
    )

    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default=DISCOUNT_PERCENT,
        verbose_name='Loại giảm giá'
    )

    discount_value = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='Giá trị giảm'
    )

    min_order_value = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Giá trị đơn tối thiểu'
    )

    max_discount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Giảm tối đa'
    )

    start_date = models.DateTimeField(
        verbose_name='Ngày bắt đầu'
    )

    end_date = models.DateTimeField(
        verbose_name='Ngày kết thúc'
    )

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Số lượt sử dụng tối đa'
    )

    used_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Đã sử dụng'
    )

    active = models.BooleanField(
        default=True,
        verbose_name='Đang hoạt động'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        now = timezone.now()

        if not self.active:
            return False

        if now < self.start_date or now > self.end_date:
            return False

        if (
            self.usage_limit is not None
            and self.used_count >= self.usage_limit
        ):
            return False

        return True

    class Meta:
        verbose_name = 'Mã khuyến mãi'
        verbose_name_plural = 'Mã khuyến mãi'


# =========================================================
# 7. ĐƠN HÀNG
# =========================================================

class Order(models.Model):

    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_SHIPPING = 'shipping'
    STATUS_DELIVERED = 'delivered'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Chờ xác nhận'),
        (STATUS_CONFIRMED, 'Đã xác nhận'),
        (STATUS_SHIPPING, 'Đang giao'),
        (STATUS_DELIVERED, 'Đã giao'),
        (STATUS_COMPLETED, 'Hoàn thành'),
        (STATUS_CANCELLED, 'Đã hủy'),
    ]

    PAYMENT_QR = 'qr'

    PAYMENT_CHOICES = [
        (PAYMENT_QR, 'Thanh toán bằng mã QR'),
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Khách hàng'
    )

    full_name = models.CharField(
        max_length=150,
        verbose_name='Họ tên người nhận'
    )

    phone = models.CharField(
        max_length=15,
        verbose_name='Số điện thoại'
    )

    address = models.TextField(
        verbose_name='Địa chỉ nhận hàng'
    )

    total = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        verbose_name='Tổng tiền'
    )

    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Mã khuyến mãi'
    )

    discount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        verbose_name='Số tiền giảm'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_QR,
        verbose_name='Phương thức thanh toán'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Trạng thái'
    )

    note = models.TextField(
        blank=True,
        verbose_name='Ghi chú'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày đặt hàng'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Ngày cập nhật'
    )

    def __str__(self):
        return f'Đơn #{self.id} - {self.customer.username}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'


# =========================================================
# 8. CHI TIẾT ĐƠN HÀNG
# =========================================================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Đơn hàng'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='Sản phẩm'
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Số lượng'
    )

    price = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='Giá bán'
    )

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    class Meta:
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'


# =========================================================
# 9. ĐÁNH GIÁ SẢN PHẨM
# =========================================================

class Review(models.Model):

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Khách hàng'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Sản phẩm'
    )

    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        verbose_name='Số sao'
    )

    comment = models.TextField(
        blank=True,
        verbose_name='Nhận xét'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày đánh giá'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Ngày cập nhật'
    )

    def __str__(self):
        return f'{self.product.name} - {self.rating} sao'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'product'],
                name='unique_customer_product_review'
            )
        ]
        ordering = ['-created_at']
        verbose_name = 'Đánh giá'
        verbose_name_plural = 'Đánh giá'