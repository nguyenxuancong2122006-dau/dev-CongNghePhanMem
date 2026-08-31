from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import (
    CustomerProfile,
    Category,
    Product,
    Cart,
    CartItem,
    Promotion,
    Order,
    OrderItem,
    Review,
)


# =========================================================
# CUSTOMER PROFILE
# =========================================================

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'phone',
        'address',
        'created_at',
    )

    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'phone',
    )

    list_filter = (
        'created_at',
    )


# =========================================================
# CATEGORY
# =========================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'created_at',
    )

    search_fields = (
        'name',
    )

    ordering = (
        '-created_at',
    )


# =========================================================
# PRODUCT
# =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'category',
        'price',
        'quantity',
        'stock_status',
        'is_active',
        'created_at',
    )

    list_filter = (
        'category',
        'is_active',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
    )

    list_editable = (
        'price',
        'quantity',
        'is_active',
    )

    ordering = (
        '-created_at',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    def stock_status(self, obj):
        if obj.quantity == 0:
            return '❌ Hết hàng'

        if obj.quantity <= 5:
            return '⚠️ Sắp hết'

        return '✅ Còn hàng'

    stock_status.short_description = 'Tình trạng kho'


# =========================================================
# CART
# =========================================================

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'total',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'user__username',
        'user__email',
    )

    inlines = [
        CartItemInline,
    ]


# =========================================================
# PROMOTION
# =========================================================

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):

    list_display = (
        'code',
        'discount_type',
        'discount_value',
        'min_order_value',
        'start_date',
        'end_date',
        'usage_limit',
        'used_count',
        'active',
        'promotion_status',
    )

    list_filter = (
        'discount_type',
        'active',
        'start_date',
        'end_date',
    )

    search_fields = (
        'code',
    )

    list_editable = (
        'active',
    )

    readonly_fields = (
        'used_count',
        'created_at',
    )

    def promotion_status(self, obj):

        if not obj.active:
            return '❌ Tắt'

        if obj.is_valid:
            return '✅ Đang hoạt động'

        return '⚠️ Hết hạn'

    promotion_status.short_description = 'Trạng thái'


# =========================================================
# ORDER ITEM
# =========================================================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'price',
    )


# =========================================================
# ORDER
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer',
        'full_name',
        'phone',
        'total',
        'payment_method',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'payment_method',
        'created_at',
    )

    search_fields = (
        'id',
        'customer__username',
        'customer__email',
        'full_name',
        'phone',
    )

    list_editable = (
        'status',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    inlines = [
        OrderItemInline,
    ]

    ordering = (
        '-created_at',
    )


# =========================================================
# REVIEW
# =========================================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer',
        'product',
        'rating',
        'comment',
        'created_at',
    )

    list_filter = (
        'rating',
        'created_at',
    )

    search_fields = (
        'customer__username',
        'customer__email',
        'product__name',
        'comment',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )


# =========================================================
# ORDER ITEM
# =========================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price',
        'subtotal_display',
    )

    search_fields = (
        'product__name',
        'order__id',
    )

    def subtotal_display(self, obj):
        return f'{obj.subtotal:,.0f} đ'

    subtotal_display.short_description = 'Thành tiền'