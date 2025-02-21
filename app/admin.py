from django.contrib import admin
from .models import OrderPlaced, Payment, Product, Customer, Cart, Wishlist
from django.utils.html import format_html
from django.urls import reverse


# Register your models here.
@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'discounted_price', 'category', 'product_image']

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','locality','city','state','zipcode']


@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'product_link']

    def product_link(self, obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])  # Correct app name
        return format_html('<a href="{}">{}</a>', link, obj.product.title)

    product_link.short_description = "Product"

@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'razorpay_order_id', 'razorpay_payment_id', 'paid']  

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):  
    list_display = ['id', 'user', 'customers', 'product', 'quantity', 'order_date', 'status', 'payment']
    
    def customers(self, obj):
        link = reverse("admin:app_customer_change", args=[obj.customer.pk])  
        return format_html('<a href="{}">{}</a>', link, obj.customer.user.username)
    def products(self, obj):
        link = reverse("admin:app_customer_change", args=[obj.customer.pk])  
        return format_html('<a href="{}">{}</a>', link, obj.product.title)


@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product_link']  

    def product_link(self, obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', link, obj.product.title)

    product_link.short_description = "Product"
    

    
    

    

