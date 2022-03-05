from django.urls import path
from . import views

urlpatterns = [
    # PAGE
    path("", views.home, name="home"),
    path("clothes/<int:pg>", views.clothes, name="clothes"),
    path("clothes/", views.clothes, name="clothes"),
    path("accessories/<int:pg>", views.accessories, name="accessories"),
    path("accessories/", views.accessories, name="accessories"),
    path("bestsellers/<int:pg>", views.bestsellers, name="bestsellers"),
    path("bestsellers/", views.bestsellers, name="bestsellers"),
    path("sale/<int:pg>", views.sale, name="sale"),
    path("sale/", views.sale, name="sale"),
    path("product/<uuid:_id>", views.product, name="product"),

    # INFO
    path("about/", views.about, name="about"),
    path("logistics/", views.logistics, name="logistics"),
    path("contact/", views.contact, name="contact"),
    path("payment_methods/", views.payment_methods, name="payment_methods"),
    path("returns/", views.returns, name="returns"),

    # USER
    path("cart/", views.cart, name="cart"),
    path("register_user/", views.register_user, name="register_user"),
    path("login_user/", views.login_user, name="login_user"),
    path("logout_user/", views.logout_user, name="logout_user"),
    path("user_page/", views.user_page, name="user_page"),
    path("edit_user/", views.edit_user, name="edit_user"),
    path("all_orders/<int:pg>", views.all_orders, name="all_orders"),
    path("all_orders/", views.all_orders, name="all_orders"),
    path("confirm_payment/", views.confirm_payment, name="confirm_payment"),
    path("verify_user/", views.verify_user, name="verify_user"),
    path("delete_user/", views.delete_user, name="delete_user"),
    path("reset_password/", views.reset_password, name="reset_password")
]
