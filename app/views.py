from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from . models import Cart, Customer, Product, Wishlist
from .forms import CustomerRegistrationForm, CostomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Create your views here.
@login_required
def home(request):
    totalitem = 0
    Wishitem=0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count() 
        wishitem= Wishlist.objects.filter(user=request.user).count() 
    return render(request,'app/home.html',locals())

@login_required
def about(request):
    totalitem = 0
    wishitem = 0  # Fixed capitalization
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()  # Fixed variable
    return render(request, 'app/about.html', {'totalitem': totalitem, 'wishitem': wishitem})  # Now included

@login_required
def contact(request):
     totalitem= 0
     wishitem=0
     if request.user.is_authenticated:
         totalitem =len( Cart.objects.filter(user=request.user))
         wishitem =len( Wishlist.objects.filter(user=request.user))
     return render(request, 'app/contact.html',locals())


@method_decorator(login_required, name="dispatch") 
class CategoryView(View):
    def get(self, request, val):
        totalitem = 0
        wishitem = 0

        # Fetch products for the given category
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')

        # Check if user is authenticated before accessing Cart and Wishlist
        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
            wishitem = Wishlist.objects.filter(user=request.user).count()

        return render(request, 'app/category.html', {
            'product': product,
            'title': title,
            'totalitem': totalitem,  # Now passed to template
            'wishitem': wishitem     # Now passed to template
        })
        
@method_decorator(login_required, name="dispatch")  
class CategoryTitle(View):
    def get(self, request, val):
            product =Product.objects.filter(title=val)
            title= Product.objects.filter(category=product[0].category).values('title')
            totalitem=0
            wishitem=0
            if request.user.is_authenticated:
                totalitem = Cart.objects.filter(user=request.user).count()
                wishitem = Wishlist.objects.filter(user=request.user).count()
            return render(request,'app/category.html',locals())


@method_decorator(login_required, name="dispatch") 
class ProductDetail(View):
     def get(self, request,pk):
         product=Product.objects.get(pk=pk)
         wishlist= Wishlist.objects.filter(Q(product=product)& Q(user=request.user))
         totalitem=0
         wishitem=0
         
         if request.user.is_authenticated:
            totalitem =len( Cart.objects.filter(user=request.user))    
            wishitem =len( Wishlist.objects.filter(user=request.user))         
         return render(request,"app/productdetail.html",locals())     


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        totalitem= 0
        wishitem=0
        if request.user.is_authenticated:
         totalitem =len( Cart.objects.filter(user=request.user))
         wishitem =len( Wishlist.objects.filter(user=request.user))
         
        return render(request, 'app/customerregistration.html',locals())

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! User Registered Successfully.")
        else:
            messages.warning(request, "Invalid Input Data.")
        return render(request, 'app/customerregistration.html', locals())


@method_decorator(login_required, name="dispatch") 
class ProfileView(View):
    def get(self, request):
        totalitem= 0
        wishitem=0
        if request.user.is_authenticated:
         totalitem =len( Cart.objects.filter(user=request.user))
         wishitem =len( Wishlist.objects.filter(user=request.user))
         form= CostomerProfileForm()
        return render(request, 'app/profile.html', locals())

    def post(self, request):
        form= CostomerProfileForm(request.POST)
        if form.is_valid():
            user= request.user
            name= form.cleaned_data['name']
            locality= form.cleaned_data['locality']
            city= form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state= form.cleaned_data['state']
            zipcode= form.cleaned_data['zipcode']

            reg = Customer(user=user, name=name, locality=locality, mobile=mobile ,city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, "congratulatiions! Profile Save Successfully")
        else:
            messages.warning(request,"Invalid Input data")
        return render(request, 'app/profile.html', locals())

@login_required
def address(request):
    totalitem= 0
    wishitem=0
    if request.user.is_authenticated:
         totalitem =len( Cart.objects.filter(user=request.user))
         wishitem =len( Wishlist.objects.filter(user=request.user))
    add=Customer.objects.filter(user=request.user)
    return render(request,'app/address.html',locals())


@method_decorator(login_required, name='dispatch')
class UpdateAddress(View):
    def get(self, request, pk):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        
        add = Customer.objects.get(pk=pk)
        form = CostomerProfileForm(instance=add)
        
        return render(request, 'app/updateAddress.html', locals())

    def post(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CostomerProfileForm(request.POST, instance=add)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! Profile updated successfully.")
            return redirect("address")  # Redirect to the address page
        else:
            messages.warning(request, "Invalid input data.")
        
        return render(request, 'app/updateAddress.html', {"form": form})

 
 
@login_required
def add_to_cart(request):
    totalitem= 0
    wishitem=0
    if request.user.is_authenticated:
         totalitem =len( Cart.objects.filter(user=request.user))
         wishitem =len( Wishlist.objects.filter(user=request.user))
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add items to the cart.")
        return redirect('login') 

    user = request.user
    product_id = request.GET.get('prod_id')

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('home')  
    

    Cart.objects.create(user=user, product=product)  
    
    return redirect("/cart")


@method_decorator(login_required, name="dispatch") 
class checkout(View):
    def get (self, request):
        totalitem= 0
        wishitem=0
        if request.user.is_authenticated:
         totalitem =len( Cart.objects.filter(user=request.user))
         wishitem =len( Wishlist.objects.filter(user=request.user))
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user) 
        famount= 0
        for p in cart_items:
            value= p.quantity* p.product.discounted_price
            famount=famount+ value
            totalamount= famount+40
        return render (request, 'app/checkout.html', locals())
    
    
@login_required
def submit_rating(request):
    totalitem= 0
    wishitem=0
    if request.user.is_authenticated:
         totalitem =len( Cart.objects.filter(user=request.user))
         wishitem =len( Wishlist.objects.filter(user=request.user))
    if request.method == "POST":
        rating = request.POST.get("rating")
        print("User Rating:", rating)
        return redirect("checkout")  
    
@login_required
def orders(request):
    totalitem = 0
    order_placed = []

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        
        try:
            order_placed = order_placed.objects.filter(user=request.user)
        except Exception as e:
            print(f"Error fetching orders: {e}")

    return render(request, 'app/orders.html', {"order_placed": order_placed, "totalitem": totalitem})


@login_required
def show_cart(request):
    totalitem = 0
    amount = 0 

    if request.user.is_authenticated:
        user = request.user
        totalitem = Cart.objects.filter(user=user).count()
        
        cart = Cart.objects.filter(user=user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)  
        
        totalamount = amount + 40 if amount > 0 else 0

    return render(request, 'app/addtocart.html', {
        'totalitem': totalitem,
        'cart': cart,
        'amount': amount,
        'totalamount': totalamount
    })

@login_required
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        C = Cart.objects.get(Q(product=prod_id) & Q(user=request.user)) 
        C.quantity += 1
        C.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount += value
        totalamount = amount + 40
        data = {
            'quantity': C.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)


@login_required
def minus_cart(request):
     if request.method == 'GET':
        prod_id = request.GET['prod_id']
        C = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))  # Fixed query syntax
        C.quantity -= 1
        C.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount += value
        totalamount = amount + 40
        data = {
            'quantity': C.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)


@login_required
def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get("prod_id") 

        C= Cart.objects.get(Q(product=prod_id)& Q(user= request.user))

        C.delete()
        user= request.user
        cart= Cart.objects.filter(user=user)
        amount=0
        for p in cart:
            value= p.quantity* p.product.discounted_price
            amount= amount+ value
            totalamount= amount+ 40
            data={
            "amount": amount,
            "totalamount": totalamount
        }
    return JsonResponse(data)




@login_required
def wishlist(request):
    user = request.user
    wishlist = Wishlist.objects.filter(user=user)  # Ensure this is a QuerySet
    totalitem = Cart.objects.filter(user=user).count()
    wishitem = wishlist.count()  # Count wishlist items

    return render(request, 'app/wishlist.html', {
        'wishlist': wishlist,
        'totalitem': totalitem,
        'wishitem': wishitem
    })



@login_required
def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')  # Get product ID from request
        user = request.user

        try:
            product = Product.objects.get(id=prod_id)  # Get the product
        except Product.DoesNotExist:
            return JsonResponse({'message': 'Product does not exist'}, status=404)

        wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)

        if created:
            message = "Product added to wishlist"
        else:
            message = "Product is already in wishlist"

        total_wishlist_items = Wishlist.objects.filter(user=user).count()

        return JsonResponse({'message': message, 'totalwishlist': total_wishlist_items})

@login_required
def minus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        user = request.user

        try:
            product = Product.objects.get(id=prod_id)
        except Product.DoesNotExist:
            return JsonResponse({'message': 'Product does not exist'}, status=404)

        wishlist_item = Wishlist.objects.filter(user=user, product=product)
        if wishlist_item.exists():
            wishlist_item.delete()
            message = "Product removed from wishlist"
        else:
            message = "Product not found in wishlist"

        total_wishlist_items = Wishlist.objects.filter(user=user).count()

        return JsonResponse({'message': message, 'totalwishlist': total_wishlist_items})
    
@login_required
def search(request):
    query = request.GET.get('search', '').strip()  # Prevent crashes on empty searches
    products = []  # Default empty list

    totalitem = 0
    wishitem = 0

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()

    if query:  # Only search if query is not empty
        products = Product.objects.filter(title__icontains=query)  # Use correct field

    return render(request, "app/search.html", {
        'products': products,
        'query': query,
        'totalitem': totalitem,
        'wishitem': wishitem
    })
