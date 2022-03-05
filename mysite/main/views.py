from .utils import Category, process_request, list_to_str, handle_file_upload,\
    paginate_user_products, mail_sender, query_by_id, query_by_category,\
    delete_from_cart, delete_promo_codes
from .models import Product, User, Cart, CartProduct, Order,\
    OrderProduct, OrderStatus, Address, Announcement, DeliveryType,\
    PromoCode, HeaderImage, SubImage
from .forms import RegisterForm, LoginForm, EditForm, AddressForm,\
    ConfirmPaymentForm, VerifyForm, ResetPasswordForm, ResetPasswordEmailForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
import threading
import secrets
import json
import math
import uuid

# Create your views here.

# For some reason windows generates token that is twice as long as defined
# Linux on the other hand generates token of exact length as specified
HEX_TOKEN_LENGTH = 4
THREADING = False


def home(request) -> render:
    products = list(Product.objects.all().order_by("-id")[:5])
    if THREADING:
        t = threading.Thread(
            daemon=True,
            target=delete_from_cart,
            args=(CartProduct.objects.all(),)
        )
        t.start()
        t1 = threading.Thread(
            daemon=True,
            target=delete_promo_codes,
            args=(PromoCode.objects.all(),)
        )
        t1.start()
    else:
        delete_from_cart(CartProduct.objects.all())
        # delete_promo_codes(PromoCode.objects.all())

    header_imgs = HeaderImage.objects.all()
    sub_imgs = SubImage.objects.all()

    prod = [
        {
            "id": p.pk,
            "name": p.name,
            "prev_price": p.previous_price,
            "price": p.price,
            "default_image": p.productimage_set.get_queryset().filter(default=True)[0].image.url,
            "sizes": list_to_str(
                [sz.size_name for sz in list(p.size_set.get_queryset()) if sz.quantity > 0]
            )
        } for p in products
    ]

    return render(request, "main/page/index.html", {
        "products": prod,
        "header_imgs": header_imgs,
        "sub_imgs": list(sub_imgs),
        "sub_imgs_len": range(math.ceil(len(sub_imgs) / 2))
    })


def clothes(request, pg: int = 1) -> render:
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    clths = query_by_category(Category.CLOTHES, q)
    processed_resp = process_request(request, clths, pg)

    return render(request, "main/page/main_page.html", {
        "page_name": "Odzież",
        "products": processed_resp["products"],
        "products_range": processed_resp["products_range"],
        "products_len_range": processed_resp["products_len_range"],
        "page_range": processed_resp["p_range"],
        "curr_page": pg,
        "num_pages": processed_resp["num_pages"],
        "resp": processed_resp["resp"],
        "q": q
    })


def accessories(request, pg: int = 1) -> render:
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    acc = query_by_category(Category.ACCESSORIES, q)
    processed_resp = process_request(request, acc, pg)

    return render(request, "main/page/main_page.html", {
        "page_name": "Akcesoria",
        "products": processed_resp["products"],
        "products_range": processed_resp["products_range"],
        "products_len_range": processed_resp["products_len_range"],
        "page_range": processed_resp["p_range"],
        "curr_page": pg,
        "num_pages": processed_resp["num_pages"],
        "resp": processed_resp["resp"],
        "q": q
    })


def bestsellers(request, pg: int = 1) -> render:
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    bstsellers = query_by_category(Category.BESTSELLERS, q)
    processed_resp = process_request(request, bstsellers, pg)

    return render(request, "main/page/main_page.html", {
        "page_name": "Bestsellery",
        "products": processed_resp["products"],
        "products_range": processed_resp["products_range"],
        "products_len_range": processed_resp["products_len_range"],
        "page_range": processed_resp["p_range"],
        "curr_page": pg,
        "num_pages": processed_resp["num_pages"],
        "resp": processed_resp["resp"],
        "q": q
    })


def sale(request, pg: int = 1) -> render:
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    sl = query_by_category(Category.SALE, q)
    processed_resp = process_request(request, sl, pg)

    return render(request, "main/page/main_page.html", {
        "page_name": "Wyprzedaże",
        "products": processed_resp["products"],
        "products_range": processed_resp["products_range"],
        "products_len_range": processed_resp["products_len_range"],
        "page_range": processed_resp["p_range"],
        "curr_page": pg,
        "num_pages": processed_resp["num_pages"],
        "resp": processed_resp["resp"],
        "q": q
    })


def product(request, _id: uuid) -> render:
    prod_dict, product = query_by_id(_id)

    # FOR TESTING PURPOSES ONLY
    if request.method == "POST":
        if request.user.is_authenticated:
            if not request.user.user.is_verified:
                messages.info(
                    request,
                    "Musisz zweryfikować swoje konto za pomocą kodu wysłanego na twój adres email"
                )
                return redirect("verify_user")

            size_nm = request.POST.get("to-cart")
            product_size = product.size_set.get(size_name=size_nm)
            # if prod_db.quantity - 1 == 0:
            #     prod_db.delete()
            # else:
            #     prod_db.quantity -= 1
            #     prod_db.save()

            create_new_product = True
            user_cart = request.user.user.cart
            user_cart_products = user_cart.cartproduct_set.get_queryset()
            cart_products = [
                (prod.product.name, prod.size.size_name) for prod in user_cart_products
            ]
            for prod in cart_products:
                name = prod[0]
                size = prod[1]
                if product.name == name and product_size.size_name == size:
                    cartproduct = CartProduct.objects.filter(product__name=name, size__size_name=size)[0]
                    quan = cartproduct.quantity
                    quan += 1
                    cartproduct.quantity = quan
                    cartproduct.save()
                    create_new_product = False

            overall_price = user_cart.overall_price
            overall_price += product.price
            user_cart.overall_price = overall_price
            user_cart.save()
            if create_new_product:
                new_product = CartProduct(cart=user_cart, product=product, size=product_size)
                new_product.save()

            quantity = product_size.quantity
            product_size.quantity = quantity - 1
            product_size.save()

            messages.success(
                request,
                f"Dodano {product.name}, rozmiar {product_size.size_name} do koszyka!"
            )
        else:
            messages.error(
                request,
                "Musisz być zalogowany/a aby dodać produkt do koszyka!"
            )
            return redirect("login_user")

        prod_dict, product = query_by_id(_id)

    return render(request, "main/page/product.html", {
        "category": prod_dict["category"].value,
        "product_name": prod_dict["name"],
        "prev_price": prod_dict["prev_price"],
        "price": prod_dict["price"],
        "desc": prod_dict["description"],
        "sizes": prod_dict["sizes_available"],
        "img_urls": prod_dict["images"],
        "img_urls_json": json.dumps(prod_dict["images"]),
        "sizing": prod_dict["sizing"].split("\n"),
        "composition": prod_dict["composition"].split("\n"),
        "product_id": _id
    })


# INFO


def about(request) -> render:
    return render(request, "main/info/about.html", {})


def logistics(request) -> render:
    return render(request, "main/info/logistics.html", {})


def contact(request) -> render:
    return render(request, "main/info/contact.html", {})


def payment_methods(request) -> render:
    return render(request, "main/info/payment-methods.html", {})


def returns(request) -> render:
    return render(request, "main/info/returns.html", {})

# END INFO

# USER


def register_user(request) -> render:
    if request.user.is_authenticated:
        return redirect("user_page")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        c = Cart(owner=email)
        c.save()

        try:
            # This is a workaround so there can't be multiple
            # instances of the same email in the database
            # fix this by adding unique=True to the User model
            # in email field
            already_exists = User.objects.filter(email=email)
            if already_exists:
                raise Exception("Email already in the database!")

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                cart=c,
                code=secrets.token_hex(HEX_TOKEN_LENGTH)
            )
            user.save()

            user_address = Address(
                user=user
            )
            user_address.save()

            user = authenticate(
                request,
                username=username,
                password=password
            )
            if user is not None:
                login(request, user)

                if THREADING:
                    t = threading.Thread(daemon=True, target=mail_sender, kwargs={
                        "subject": f"Weryfikacja użytkownika {request.user.username}",
                        "header": "Zweryfikuj swoje konto",
                        "msg": "Aby dokończyć proces rejestracji wpisz na stronie podany poniżej kod",
                        "add_content": request.user.user.code,
                        "user": request.user
                    })
                    t.start()
                else:
                    mail_sender(
                        subject=f"Weryfikacja użytkownika {request.user.username}",
                        header="Zweryfikuj swoje konto",
                        msg="Aby dokończyć proces rejestracji wpisz na stronie podany poniżej kod",
                        add_content=request.user.user.code,
                        user=request.user
                    )
                # send_verification(user=request.user)

                if not request.user.user.is_verified:
                    messages.info(request, "Musisz zweryfikować swoje konto za pomocą kodu wysłanego na twój adres email")
                    return redirect("verify_user")

                # user_address = request.user.address_set.get_queryset()[0]
                if not user.user.first_name or not user.user.last_name:
                    messages.info(request, "Uzupełnij swoje dane")
                    return redirect("edit_user")

                messages.success(request, "Pomyślnie zarejestrowano!")
                return redirect("user_page")
        except Exception as e:
            if "username" in str(e):
                msg = "Nazwa użytkownika zajęta!"
            elif "Email" in str(e):
                msg = "Adres e-mail zajęty!"
            messages.error(request, msg)

    register_form = RegisterForm()

    return render(request, "main/user/register-login.html", {
        "form": register_form,
        "type": "register"
    })


def verify_user(request) -> render:
    if not request.user.is_authenticated:
        return redirect("login_user")

    if request.method == "POST":
        code = request.POST.get("code")
        if request.user.user.code == code:
            request.user.user.is_verified = True
            request.user.user.save()
            messages.success(request, "Twoje konto zostało zweryfikowane")
            return redirect("user_page")
        else:
            messages.error(request, "Niepoprawny kod weryfikacyjny!")

    form = VerifyForm()
    return render(request, "main/user/verify_user.html", {
        "form": form
    })


def delete_user(request) -> render:
    if not request.user.is_authenticated:
        return redirect("login_user")

    if request.method == "POST":
        code = request.POST.get("code")
        if request.user.user.code == code:
            request.user.user.cart.delete()
            messages.success(request, "Twoje konto zostało usunięte.")
            return redirect("home")
        else:
            messages.error(request, "Niepoprawny kod weryfikacyjny!")

    form = VerifyForm()
    return render(request, "main/user/delete_user.html", {
        "form": form
    })


def login_user(request) -> render:
    username = None

    if request.user.is_authenticated:
        return redirect("user_page")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(
            request,
            username=username,
            password=password
        )
        if user is not None:
            login(request, user)
            if user.is_superuser:
                redirect("home")

            if not request.user.user.is_verified:
                messages.info(
                    request,
                    "Musisz zweryfikować swoje konto za pomocą kodu wysłanego na twój adres email"
                )
                return redirect("verify_user")

            # user_address = Address.objects.filter(user=request.user)
            if not user.user.first_name or not user.user.last_name:
                messages.info(request, "Uzupełnij swoje dane")
                return redirect("edit_user")

            messages.success(request, "Pomyślnie zalogowano!")
            return redirect("user_page")
        else:
            messages.error(request, "Niepoprawne dane logowania!")

    if username:
        login_form = LoginForm()
        login_form.fields["username"].widget.attrs["value"] = username
    else:
        login_form = LoginForm()

    return render(request, "main/user/register-login.html", {
        "form": login_form,
        "type": "login"
    })


def logout_user(request) -> render:
    if not request.user.is_authenticated:
        return redirect("login_user")

    logout(request)
    messages.add_message(request, messages.SUCCESS, "Pomyślnie wylogowano!")
    return redirect("home")


def reset_password(request) -> render:
    if request.user.is_authenticated:
        if request.method == "POST":
            pwd = request.POST.get("password")
            confirm_pwd = request.POST.get("confirm_password")

            if pwd == confirm_pwd:
                uname = request.user.username
                request.user.set_password(pwd)
                request.user.save()

                user = authenticate(
                    request,
                    username=uname,
                    password=pwd
                )
                if user is not None:
                    login(request, user)

                messages.success(request, "Ustawiono nowe hasło.")
                return redirect("user_page")
            else:
                messages.error(request, "Hasła nie zgadzają się ze sobą!")

        form = ResetPasswordForm()

        return render(request, "main/user/reset_password.html", {
            "form": form,
            "logged_in": True
        })
    else:
        if request.method == "POST":
            mail = request.POST.get("mail")
            code = request.POST.get("code")

            user_query = User.objects.filter(email=mail)

            if user_query:
                if not code:
                    user_query[0].user.code = secrets.token_hex(HEX_TOKEN_LENGTH)
                    user_query[0].user.save()
                    messages.success(
                        request,
                        "Wysłaliśmy kod weryfikacyjny na twój adres email."
                    )

                if code == user_query[0].user.code:
                    user_query[0].backend = "django.contrib.auth.backends.ModelBackend"
                    login(request, user_query[0])

                    messages.success(request, "Kod poprawny, możesz zmienić swoje hasło.")
                    return redirect("reset_password")

                if THREADING:
                    t = threading.Thread(daemon=True, target=mail_sender, kwargs={
                        "subject": f"Reset hasła użytkownika {user_query[0].user.username}",
                        "header": "Zresetuj swoje hasło",
                        "msg": "Aby dokończyć reset hasła wpisz na stronie podany poniżej kod",
                        "add_content": user_query[0].user.code,
                        "user": user_query[0]
                    })
                    t.start()
                else:
                    mail_sender(
                        subject=f"Reset hasła użytkownika {user_query[0].user.username}",
                        header="Zresetuj swoje hasło",
                        msg="Aby dokończyć reset hasła wpisz na stronie podany poniżej kod",
                        add_content=user_query[0].user.code,
                        user=user_query[0]
                    )

                form = ResetPasswordEmailForm()
                verify_form = VerifyForm()

                if mail:
                    form.fields['mail'].widget.attrs['value'] = mail

                return render(request, "main/user/reset_password.html", {
                    "form": form,
                    "verify_form": verify_form,
                })

            messages.error(request, "Nie istnieje użytkownik o podanym emailu!")

        form = ResetPasswordEmailForm()

        return render(request, "main/user/reset_password.html", {
            "form": form
        })


def user_page(request) -> render:
    if not request.user.is_authenticated:
        return redirect("login_user")

    if not request.user.user.is_verified:
        messages.info(
            request,
            "Musisz zweryfikować swoje konto za pomocą kodu wysłanego na twój adres email"
        )
        return redirect("verify_user")

    new_info = Announcement.objects.all().order_by("-id")[:6]

    print(request.user.pk)

    orders = []
    orders_set = request.user.user.order_set.get_queryset()
    show_more = False
    if orders_set:
        queryset = list(orders_set)
        if len(queryset) > 3:
            show_more = True
            for _ in range(3):
                orders.append(queryset.pop())
        else:
            orders = queryset[::-1]

    return render(request, "main/user/user_page.html", {
        "orders": orders,
        "new_info": new_info,
        "show_more": show_more
    })


def edit_user(request) -> render:
    if not request.user.is_authenticated:
        return redirect("login_user")

    if not request.user.user.is_verified:
        messages.info(
            request,
            "Musisz zweryfikować swoje konto za pomocą kodu wysłanego na twój adres email"
        )
        return redirect("verify_user")

    if request.method == "POST":
        new_details = {
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name"),
            "phone": request.POST.get("phone"),
            "city": request.POST.get("city"),
            "zipcode": request.POST.get("zipcode"),
            "address": request.POST.get("address")
        }

        user = request.user.user
        user_address = request.user.user.address_set.get_queryset()[0]

        edited_user = False
        edited_address = False
        for k, v in new_details.items():
            if v is None:
                del new_details[k]
                continue
            if k in user.__dict__:
                if v != user.__dict__[k]:
                    user.__dict__[k] = v
                    if not edited_user:
                        edited_user = True
            elif k in user_address.__dict__:
                if v != user_address.__dict__[k]:
                    user_address.__dict__[k] = v
                    if not edited_address:
                        edited_address = True

        if edited_user:
            user.save()
            # messages.success(request, "Twoje dane osobowe zostały zmienione.")
        if edited_address:
            user_address.save()

        if edited_user or edited_address:
            messages.success(request, "Twoje dane osobowe zostały zmienione.")
            return redirect("user_page")

    edit_form = EditForm()
    edit_form.fields["first_name"].widget.attrs["value"] = request.user.user.first_name
    edit_form.fields["last_name"].widget.attrs["value"] = request.user.user.last_name
    edit_form.fields["phone"].widget.attrs["value"] = request.user.user.phone
    edit_form.fields["first_name"].widget.attrs["placeholder"] = "Wpisz swoje imię"
    edit_form.fields["last_name"].widget.attrs["placeholder"] = "Wpisz swoje nazwisko"
    edit_form.fields["phone"].widget.attrs["placeholder"] = "Wpisz swój numer telefonu"

    address_form = AddressForm()
    address_form.fields["city"].widget.attrs["value"] =\
        request.user.user.address_set.get_queryset()[0].city
    address_form.fields["zipcode"].widget.attrs["value"] =\
        request.user.user.address_set.get_queryset()[0].zipcode
    address_form.fields["address"].widget.attrs["value"] =\
        request.user.user.address_set.get_queryset()[0].address
    address_form.fields["city"].widget.attrs["placeholder"] = "Wpisz swoje miasto"
    address_form.fields["zipcode"].widget.attrs["placeholder"] = "Wpisz swój kod pocztowy"
    address_form.fields["address"].widget.attrs["placeholder"] = "Wpisz swoją ulicę i numer domu lub mieszkania"

    return render(request, "main/user/edit_user.html", {
        "user_form": edit_form,
        "address_form": address_form
    })


def cart(request) -> render:
    if not request.user.is_authenticated:
        return redirect("login_user")

    if not request.user.user.is_verified:
        messages.info(
            request,
            "Musisz zweryfikować swoje konto za pomocą kodu wysłanego na twój adres email"
        )
        return redirect("verify_user")

    user_cart = request.user.user.cart

    # If deleting items from cart
    if request.method == "POST" and request.POST.get("delete-item"):
        to_delete = request.POST.get("delete-item")
        item = CartProduct.objects.filter(pk=to_delete)[0]

        # Quantity of a size of a product +1
        # After removal from user cart
        size = item.product.size_set.get_queryset().filter(
            size_name=item.size.size_name,
        )[0]
        quantity = size.quantity
        size.quantity = quantity + 1
        size.save()

        overall_price = user_cart.overall_price
        overall_price -= item.product.price
        user_cart.overall_price = overall_price
        user_cart.save()

        item_quantity = item.quantity
        if item_quantity > 1:
            item_quantity -= 1
            item.quantity = item_quantity
            item.save()
        else:
            item.delete()
        messages.info(request, "Produkt usunięty z koszyka.")

    products = {}
    overall_price = float(user_cart.overall_price)
    cart_products = request.user.user.cart.cartproduct_set.get_queryset()

    for product in cart_products:
        default_image = product.product.productimage_set.get_queryset().filter(
            default=True
        )[0].image.url
        products[product] = default_image

    deliv = request.GET.get("delivery")
    if deliv:
        deliv_price = float(DeliveryType.objects.filter(delivery=deliv)[0].price)
        overall_price += deliv_price
    else:
        deliv = "Delivery.INPOSTCOURIER"
        deliv_price = float(DeliveryType.objects.filter(delivery=deliv)[0].price)
        overall_price += deliv_price

    # If order button is clicked
    if request.method == "POST" and not request.POST.get("delete-item"):
        if not request.user.is_authenticated:
            return redirect("login_user")

        if not request.user.user.is_verified:
            messages.info(
                request,
                "Musisz zweryfikować swoje konto za pomocą kodu wysłanego na twój adres email"
            )
            return redirect("verify_user")

        parcel = request.POST.get("selected_parcel")
        status = place_order(request, overall_price, deliv, parcel)
        if status == "confirm_payment":
            user_cart.overall_price = 0
            user_cart.save()
            return redirect("confirm_payment")
        else:
            return redirect(status)

    return render(request, "main/user/cart.html", {
        "products": products,
        "overall_price": round(overall_price, 2),
        "selected_delivery": deliv
    })


def place_order(request, price, delivery, parcel) -> str:
    if request.method == "POST" and request.user.user.first_name and\
            request.user.user.last_name:

        user_address = request.user.user.address_set.get_queryset()[0]

        if delivery == "Delivery.INPOSTPARCEL" and parcel == "none":
            messages.error(request, "Musisz wybrać paczkomat!")
            return "cart"

        delivery_type = DeliveryType.objects.filter(delivery=delivery)[0]
        new_order_status = OrderStatus.objects.filter(status="Status.PAYMENT")[0]
        new_order = Order(
            user=request.user.user,
            price=price,
            status=new_order_status,
            delivery=delivery_type,
            parcel=parcel
        )
        new_order.save()

        order_queryset = request.user.user.cart.cartproduct_set.get_queryset()
        for product in order_queryset:
            prod = product.product
            quan = prod.amount_sold
            prod.amount_sold = quan + 1
            prod.save()
            new_order_product = OrderProduct(
                order=new_order,
                product=product.product,
                size=product.size,
                quantity=product.quantity
            )
            new_order_product.save()

            request.user.user.cart.cartproduct_set.get_queryset().filter(
                product=product.product,
                size=product.size
            )[0].delete()

        if THREADING:
            t1 = threading.Thread(daemon=True, target=mail_sender, kwargs={
                "subject": f"Zamówienie nr {new_order.pk}",
                "header": f"Zamówienie nr {new_order.pk}",
                "order": new_order,
                "user": request.user,
                "msg": "Twoje zamówienie zostało przyjęte i przekazane do realizacji.",
                "add_content": "Dziękujemy za wspólne zakupy!",
                "delivery": delivery_type
            })
            t1.start()

            t2 = threading.Thread(daemon=True, target=mail_sender, kwargs={
                "subject": f"Użytkownik {request.user.username} złożył zamówienie",
                "header": f"Użytkownik {request.user.username} złożył zamówienie",
                "order": new_order,
                "user": request.user,
                "msg": "Zamówienie",
                "self_mail": True,
                "delivery": delivery_type
            })
            t2.start()
        else:
            mail_sender(
                subject=f"Zamówienie nr {new_order.pk}",
                header=f"Zamówienie nr {new_order.pk}",
                order=new_order,
                user=request.user,
                msg="Twoje zamówienie zostało przyjęte i przekazane do realizacji.",
                add_content="Dziękujemy za wspólne zakupy!",
                delivery=delivery_type
            )
            mail_sender(
                subject=f"Użytkownik {request.user.username} złożył zamówienie",
                header=f"Użytkownik {request.user.username} złożył zamówienie",
                order=new_order,
                user=request.user,
                msg="Zamówienie",
                self_mail=True,
                delivery=delivery_type
            )

        messages.success(request, "Zamówienie zostało złożone!")
        return "confirm_payment"

    messages.error(request, "Przed złożeniem zamówienia musisz uzupełnić swoje dane!")
    return "edit_user"


def confirm_payment(request) -> render:
    if not request.user.is_authenticated:
        return redirect("login_user")

    if not request.user.user.is_verified:
        messages.info(
            request,
            "Musisz zweryfikować swoje konto za pomocą kodu wysłanego na twój adres email"
        )
        return redirect("verify_user")

    # If redirected from place_order() order is equal to
    # most recent order in user orders
    # if get request from user_page then it gets the order id from button
    # and queries the order under that id
    product_id = request.GET.get("order-id")
    if product_id:
        order = Order.objects.filter(pk=product_id)[0]
    else:
        order = request.user.user.order_set.get_queryset().order_by("-id")[0]

    if request.method == "POST":
        file_extension = str(request.FILES.get("file")).split(".")[1]
        form = ConfirmPaymentForm(request.POST, request.FILES)

        if form.is_valid():
            filename = handle_file_upload(
                request.FILES["file"],
                request.user.user.email,
                order.pk,
                file_extension
            )

            if THREADING:
                t2 = threading.Thread(daemon=True, target=mail_sender, kwargs={
                    "subject": f"Użytkownik {request.user.username} potwierdził płatność",
                    "header": f"Użytkownik {request.user.username} potwierdził płatność",
                    "user": request.user,
                    "msg": "Płatność",
                    "self_mail": True,
                    "attachment": True,
                    "filename": f"payments/{filename}"
                })
                t2.start()
            else:
                mail_sender(
                    subject=f"Użytkownik {request.user.username} potwierdził płatność",
                    header=f"Użytkownik {request.user.username} potwierdził płatność",
                    user=request.user,
                    msg="Płatność",
                    self_mail=True,
                    attachment=True,
                    filename=f"payments/{filename}"
                )

            messages.success(request, "Potwierdzenie zapłaty przesłane!")
            new_status = OrderStatus.objects.filter(status="Status.ACCEPTED")[0]
            order.payment_confirmed = True
            order.status = new_status
            order.save()
            return redirect("user_page")

    form = ConfirmPaymentForm()
    return render(request, "main/user/confirm_payment.html", {
        "form": form,
        "order": order
    })


def all_orders(request, pg: int = 1) -> render:
    if not request.user.is_authenticated:
        redirect("login_user")

    if not request.user.user.is_verified:
        messages.info(
            request,
            "Musisz zweryfikować swoje konto za pomocą kodu wysłanego na twój adres email"
        )
        return redirect("verify_user")

    orders = request.user.user.order_set.get_queryset().order_by("-id")
    orders = paginate_user_products(orders, pg)

    return render(request, "main/user/all_orders.html", {
        "orders": orders["products"],
        "num_pages": orders["num_pages"],
        "page_range": orders["p_range"],
        "curr_page": pg
    })

# END USER
