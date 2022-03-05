from django.contrib.auth.models import User as usr
from datetime import datetime, timedelta
from django.core.files import File
from django.db import models
from io import BytesIO
from PIL import Image
import uuid

# Create your models here.


class Category(models.Model):
    cat = models.CharField(max_length=30)
    string = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.string}"


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    # slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    previous_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    desc = models.TextField()
    sizing = models.TextField()
    composition = models.TextField()
    amount_sold = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.category}"


class Size(models.Model):
    size_name = models.CharField(max_length=15)
    quantity = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.size_name}"


class HeaderImage(models.Model):
    image = models.ImageField(upload_to='headerImages')

    def save(self):
        if not self.id:
            self.image = self.compressImage(self.image)
        super(HeaderImage, self).save()

    def compressImage(self, image):
        img = Image.open(image).convert("RGB")
        im_io = BytesIO()

        img.save(im_io, format='jpeg', optimize=True, quality=50)
        new_image = File(im_io, name=f"{image.name.split('.')[0]}.jpeg")

        return new_image


class SubImage(models.Model):
    image = models.ImageField(upload_to='subImages')
    href = models.TextField(null=True, blank=True)

    def save(self):
        if not self.id:
            self.image = self.compressImage(self.image)
        super(SubImage, self).save()

    def compressImage(self, image):
        img = Image.open(image).convert("RGB")
        im_io = BytesIO()

        img.save(im_io, format='jpeg', optimize=True, quality=50)
        new_image = File(im_io, name=f"{image.name.split('.')[0]}.jpeg")

        return new_image


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    default = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products')

    def __str__(self):
        return f"{self.product.name} Image"

    def save(self):
        if not self.id:
            self.image = self.compressImage(self.image)
        super(ProductImage, self).save()

    def compressImage(self, image):
        img = Image.open(image).convert("RGB")
        im_io = BytesIO()

        img.save(im_io, format='jpeg', optimize=True, quality=50)
        new_image = File(im_io, name=f"{image.name.split('.')[0]}.jpeg")

        return new_image


# class Address(models.Model):
#     city = models.CharField(max_length=255)
#     zipcode = models.CharField(max_length=6)
#     address = models.CharField(max_length=255)


class Cart(models.Model):
    owner = models.CharField(max_length=255)
    overall_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.owner} - Cart"


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    # date_str = models.CharField(max_length=50)
    date = models.DateTimeField()
    deletion_date = models.CharField(max_length=50)
    deletion_time = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        time = datetime.now()
        date = time + timedelta(days=1)
        deletion_date = date.strftime("%d-%m-%Y")
        deletion_time = date.strftime("%H:%M")

        # time_formatted = time.strftime("%Y-%m-%d %H:%M:%S")
        if not self.id:
            self.date = time
            self.deletion_date = deletion_date
            self.deletion_time = deletion_time
        return super(CartProduct, self).save(*args, **kwargs)


class User(usr):
    usr._meta.get_field("username").verbose_name = "Nazwa użytkownika"
    usr._meta.get_field("password").verbose_name = "Hasło"
    usr._meta.get_field("email").verbose_name = "Email"
    usr._meta.get_field("first_name").verbose_name = "Imię"
    usr._meta.get_field("last_name").verbose_name = "Nazwisko"
    phone = models.CharField(max_length=255, verbose_name="Numer telefonu")
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    code = models.CharField(max_length=8)


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=255, verbose_name="Miasto")
    zipcode = models.CharField(max_length=6, verbose_name="Kod pocztowy")
    address = models.CharField(max_length=255, verbose_name="Ulica i numer domu / mieszkania")


class DeliveryType(models.Model):
    delivery = models.CharField(max_length=30)
    string = models.CharField(max_length=30)
    price = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.string}"


class OrderStatus(models.Model):
    status = models.CharField(max_length=30)
    string = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.string}"


# Order should probably have a cart instead of products
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    order_date = models.CharField(max_length=50, editable=False)
    delivery = models.ForeignKey(DeliveryType, on_delete=models.CASCADE)
    payment_confirmed = models.BooleanField(default=False)
    parcel = models.CharField(max_length=15, null=True, blank=True)

    def save(self, *args, **kwargs):
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.id:
            self.order_date = time
        return super(Order, self).save(*args, **kwargs)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class Announcement(models.Model):
    text = models.TextField()
    is_important = models.BooleanField(default=False)
    href = models.TextField(null=True, blank=True)
    announcement_date = models.CharField(max_length=50, editable=False)

    def __str__(self):
        return f"{self.announcement_date} - {self.text}"

    def save(self, *args, **kwargs):
        time = datetime.now().strftime("%d-%m-%Y")
        if not self.id:
            self.announcement_date = time
        return super(Announcement, self).save(*args, **kwargs)


class PromoCode(models.Model):
    promo_code = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now_add=True)
    expires_in = models.IntegerField(default=3)

    # def save(self, *args, **kwargs):
    #     time = datetime.now()

    #     # time_formatted = time.strftime("%Y-%m-%d %H:%M:%S")
    #     if not self.id:
    #         self.date = time
    #     return super(PromoCode, self).save(*args, **kwargs)
