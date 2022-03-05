from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.utils.html import strip_tags
from datetime import datetime, timedelta
from django.db.models import Q
from django.core import mail
from enum import Enum, auto
from .models import Product
import math
import uuid
import os


class Category(Enum):
    CLOTHES = auto()
    ACCESSORIES = auto()
    BESTSELLERS = auto()
    SALE = auto()


class Status(Enum):
    PAYMENT = auto()
    ACCEPTED = auto()
    SENT = auto()
    COMPLETED = auto()


class Delivery(Enum):
    INPOSTPARCEL = auto()
    INPOSTCOURIER = auto()
    PICKUP = auto()


def query_by_id(_id: uuid) -> tuple:
    prod = get_object_or_404(Product, pk=_id)
    sizes_available = list(prod.size_set.get_queryset().exclude(quantity=0))
    images = list(prod.productimage_set.get_queryset())
    return {
            "id": prod.pk,
            "category": convert_to_enum(prod.category.cat),
            "name": prod.name,
            "prev_price": prod.previous_price,
            "price": prod.price,
            "description": prod.desc,
            "sizes_available": sizes_available,
            "images": [img.image.url for img in images],
            "sizing": prod.sizing,
            "composition": prod.composition
    }, prod


def query_by_category(cat: Category, q: str) -> list:
    if q:
        if cat != Category.BESTSELLERS:
            prod = Product.objects.filter(
                Q(name__icontains=q) |
                Q(desc__icontains=q),
                category__cat=str(cat)
            )
        else:
            prod = Product.objects.filter(
                Q(name__icontains=q) |
                Q(desc__icontains=q)
            )
    else:
        if cat is Category.BESTSELLERS:
            prod = Product.objects.all().order_by("amount_sold")[:9]
        else:
            prod = list(Product.objects.filter(category__cat=str(cat)))
        
    prod_dict = {
        product: list(product.size_set.get_queryset().exclude(quantity=0)) for product in prod
    }

    return [
        {
            "id": p.pk,
            "category": convert_to_enum(p.category.cat),
            "name": p.name,
            "prev_price": p.previous_price,
            "price": p.price,
            "default_image": p.productimage_set.get_queryset().filter(default=True)[0].image.url,
            "sizes": list_to_str(
                [sz.size_name for sz in list(p.size_set.get_queryset()) if sz.quantity > 0]
            ),
            "amount_sold": p.amount_sold,
            "availability": True if prod_dict[p] else False
        } for p in prod
    ]


def mail_sender(
    order=None,
    user=None,
    msg=None,
    subject=None,
    header=None,
    add_content=None,
    self_mail=False,
    attachment=False,
    filename=None,
    delivery=None
):
    subject = subject + " - Hello Butik"
    html_message = render_to_string(
        "main/emails/base_email.html", {
            "header": header,
            "msg": msg,
            "user": user,
            "order": order,
            "order_price": round(float(order.price), 2) if order else None,
            "add_content": add_content,
            "self_mail": self_mail,
            "delivery": delivery
        }
    )
    plain_message = strip_tags(html_message)
    from_email = "hellobutik.pl@gmail.com"
    if self_mail:
        to = "dwronska125@wp.pl"
    else:
        to = user.user.email

    if filename:
        email = mail.EmailMessage(
            subject=subject,
            from_email=from_email,
            to=[to],
        )
        email.attach_file(filename)
        email.send()

    else:
        mail.send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to],
            html_message=html_message
        )


def delete_from_cart(cart_products):
    for cart_product in cart_products:
        elapsed = datetime.now() - cart_product.date.replace(tzinfo=None)
        if elapsed.days >= 1:
            size = cart_product.product.size_set.get_queryset().filter(
                size_name=cart_product.size.size_name,
            )[0]

            quantity = size.quantity
            size.quantity = quantity + cart_product.quantity

            # This resets the overall price of the cart
            cart_price = cart_product.cart.overall_price
            to_subtract = cart_product.product.price * cart_product.quantity
            new_cart_price = cart_price - to_subtract
            cart_product.cart.overall_price = new_cart_price
            cart_product.cart.save()

            cart_product.delete()
            size.save()


def delete_promo_codes(promo_codes):
    for promo_code in promo_codes:
        elapsed = (promo_code.date.replace(tzinfo=None) + timedelta(days=promo_code.expires_in)) -\
            datetime.now()
        print(elapsed)
        if elapsed.days < 0:
            promo_code.delete()


def sort(li: list, resp: str) -> list:
    if resp == "descending":
        li = sorted(li, key=lambda x: x["price"])
    elif resp == "ascending":
        li = sorted(li, key=lambda x: x["price"], reverse=True)

    # Show available items first
    li = sorted(li, key=lambda x: x["availability"])
    return li


def convert_to_enum(cat: str) -> Category:
    if str(cat) == "Category.CLOTHES":
        return Category.CLOTHES
    elif str(cat) == "Category.ACCESSORIES":
        return Category.ACCESSORIES
    elif str(cat) == "Category.BESTSELLERS":
        return Category.BESTSELLERS
    elif str(cat) == "Category.SALE":
        return Category.SALE
    elif str(cat) == "Status.ACCEPTED":
        return Status.ACCEPTED
    elif str(cat) == "Status.SENT":
        return Status.SENT
    elif str(cat) == "Status.COMPLETE":
        return Status.COMPLETE


def str_to_list(st: str) -> list:
    return st.split()


def list_to_str(li: list) -> str:
    return ", ".join(li)


def process_request(
    request,
    products: list,
    pg: int,
    query: str = None,
    resp: str = None,
    p_range: int = None,
    num_pages: int = None
) -> dict:
    if request.method == "POST":
        resp = request.POST.get("sort-btn")
        # query = request.POST.get("search-inp")
        # if query == "":
        #     query = None
        # if query is None:
        #     query = request.POST.get("submit-btn")

    products = sort(products, resp)

    # pagination will only occur when
    # there's no query and no resp
    # if not query and 
    if not resp:
        p = Paginator(products, 15)
        num_pages = p.num_pages
        p_range = p.page_range
        products = p.page(pg).object_list

    # this determines how many products there are
    # displayed in a single line (div)
    products_len_range = range(math.ceil(len(products) / 3))
    products_range = range(len(products))

    return {
        "products": products,
        "products_len_range": products_len_range,
        "products_range": products_range,
        "p_range": p_range,
        "num_pages": num_pages,
        "resp": resp,
    }


def paginate_user_products(products: list, pg: int):
    p = Paginator(products, 10)
    num_pages = p.num_pages
    p_range = p.page_range
    products = p.page(pg).object_list

    return {
        "products": products,
        "num_pages": num_pages,
        "p_range": p_range
    }


def handle_file_upload(file, email, order_id, ext):
    filename = f"Zamówienie nr {order_id} - {email}.{ext}"

    if not os.path.exists("payments"):
        os.mkdir("payments")
    with open(f"payments/{filename}", "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return filename
