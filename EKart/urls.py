from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('shop/', include("shop.urls")),
    # path('blog/', include("blog.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "E-Kart Admin"
admin.site.site_title = "E-Kart Admin Portal"
admin.site.index_title = "Welcome to E-Kart Admin Portal"