from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
                  path("", views.index, name="blogHome"),
                  path("blogposts/<int:blogid>", views.blogposts, name="blogpost")
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
