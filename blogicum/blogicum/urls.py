from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


handler403 = 'pages.views.csrf_failure'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('', include('blog.urls', namespace='blog')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
