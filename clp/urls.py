from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from blogs.sitemaps import BlogPostSitemap
from django.http import HttpResponse

def robots_txt(request):
    content = (
        "User-Agent: *\n"
        "Disallow: /spr-82hxQv/\n"
        "Allow: /\n"
        "Sitemap: https://clpguitar.com/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")

sitemaps = {
    "posts": BlogPostSitemap,
}

urlpatterns = [
    path('spr-82hxQv/', admin.site.urls),
    path('', include('home.urls', namespace='home')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('blogs/', include('blogs.urls', namespace='blogs')),
    path('products/', include('products.urls', namespace='products')),
    path('cart/', include('carts.urls', namespace='carts')),
    path("orders/", include("orders.urls", namespace="orders")),

    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'home.views.custom_404'
