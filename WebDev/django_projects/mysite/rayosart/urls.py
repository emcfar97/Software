from django.views.generic import RedirectView
# from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'rayosart'
urlpatterns = [
    # url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
    path('', views.IndexView.as_view(), name='index'),
    path('gallery', views.GalleryView.as_view(), name='gallery'),
    path('shop', views.ShopView.as_view(), name='shop'),
    path('about', views.AboutView.as_view(), name='about'),
    path('contact', views.ContactView.as_view(), name='contact'),
    path('cart', views.CartView.as_view(), name='cart'),
    path('checkout', views.CheckoutView.as_view(), name='checkout'),
    path('account', views.AccountView.as_view(), name='account'),
    path('product/<int:product_id>', views.ProductView.as_view()),
]