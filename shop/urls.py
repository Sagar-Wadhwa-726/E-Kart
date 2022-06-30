from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="shophome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="SearchProduct"),
    path("products/<int:myid>", views.products, name="ViewProduct"),
    path("checkout/", views.checkout, name="Checkout"),
    path("handleRequest/", views.handleRequest, name='handleRequest'),
    path("signUp/",views.signUp,name="signUp"),
    path("signIn/",views.signIn,name="signIn"),
    path("logout_handler/",views.logout_handler,name="logout_handler"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
