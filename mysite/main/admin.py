from django.contrib import admin
from .models import Product, Cart, Order, User, Category,\
    Size, ProductImage, CartProduct, OrderStatus, OrderProduct,\
    Address, Announcement, DeliveryType, PromoCode, HeaderImage, SubImage

# Register your models here.


class SizeAdmin(admin.ModelAdmin):
    list_display = ("size_name", "quantity", "product")
    list_filter = ("size_name", "quantity", "product")


class SizeInline(admin.StackedInline):
    model = Size
    max_num = 5
    extra = 0


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "default", "image")
    list_filter = ("product", "default")


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    max_num = 5
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "previous_price", "price")
    list_filter = ("price",)
    # prepopulated_fields = {"slug": ("name", "tags")}
    inlines = [SizeInline, ProductImageInline]


class CartProductInline(admin.StackedInline):
    model = CartProduct
    max_num = 100
    extra = 0


class CartAdmin(admin.ModelAdmin):
    inlines = [CartProductInline]


class OrderProductInline(admin.StackedInline):
    model = OrderProduct
    max_num = 100
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "get_username", "get_email", "price", "get_status")

    def get_username(self, obj):
        return obj.user.username
    get_username.admin_order_field = "Nazwa użytkownika"
    get_username.short_description = "Nazwa użytkownika"

    def get_email(self, obj):
        return obj.user.email
    get_email.admin_order_field = "Email"
    get_email.short_description = "Email"

    def get_status(self, obj):
        return obj.status.string
    get_status.admin_short_field = "Status zamówienia"
    get_status.short_description = "Status zamówienia"

    inlines = [OrderProductInline]


class OrderInline(admin.StackedInline):
    model = Order
    max_num = 1000
    extra = 0


class AddressInline(admin.StackedInline):
    model = Address
    max_num = 1
    extra = 0


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "email", "phone", "is_verified")
    list_filter = ("is_verified",)
    inlines = [OrderInline, AddressInline]


# class AddressInline(admin.StackedInline):
#     model = User
#     max_num = 1
#     extra = 0


# class CartAdmin(admin.ModelAdmin):
#     list_display = ("owner",)


admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Category)
admin.site.register(Size, SizeAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(CartProduct)
admin.site.register(OrderStatus)
admin.site.register(OrderProduct)
admin.site.register(Address)
admin.site.register(Announcement)
admin.site.register(DeliveryType)
admin.site.register(PromoCode)
admin.site.register(HeaderImage)
admin.site.register(SubImage)
