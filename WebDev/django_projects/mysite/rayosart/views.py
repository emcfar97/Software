from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from .models import Account, Product
class IndexView(generic.ListView):
    template_name = 'rayosart/index.html'
    
    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)
    
    def get_queryset(self): pass
    
class GalleryView(generic.ListView):
    template_name = 'rayosart/gallery.html'
    
    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)
    
    def get_queryset(self): pass
    
class ShopView(generic.ListView):
    template_name = 'rayosart/shop.html'
    
    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)
    
    def get_queryset(self): pass
    
class AboutView(generic.ListView):
    template_name = 'rayosart/about.html'
    
    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)
    
    def get_queryset(self): pass
    
class ContactView(generic.ListView):
    template_name = 'rayosart/contact.html'
    
    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)
    
    def get_queryset(self): pass
    
class CartView(generic.ListView):
    template_name = 'rayosart/cart.html'
    
    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)
    
    def get_queryset(self): pass
   
class CheckoutView(generic.ListView):
    template_name = 'rayosart/checkout.html'
    
    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)
    
    def get_queryset(self): pass
    
class AccountView(generic.ListView):
    model = Account
    template_name = 'rayosart/account.html'
    
    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)
    
    def get_queryset(self): pass
    
class ProductView(generic.DetailView):
    model = Product
    template_name = 'rayosart/product.html'
    
    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)
    
    def get_queryset(self): pass