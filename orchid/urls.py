import forms_builder.forms.urls  # add this import
import dimension.urls
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'orchid.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    (r'', include('core.urls')),
    url(r'^forms/', include(forms_builder.forms.urls)),
    url(r'^forms/', include(forms_builder.forms.urls)),
    url(r'^dimension/', include(dimension.urls, namespace="dimension")),
    url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
