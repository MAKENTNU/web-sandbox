from decorator_include import decorator_include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView

from util.url_utils import ckeditor_uploader_urls, debug_toolbar_urls, logout_urls, permission_required_else_denied
from . import views


urlpatterns = [
    path("robots.txt", TemplateView.as_view(template_name='internal/robots.txt', content_type='text/plain')),
    path(".well-known/security.txt", TemplateView.as_view(template_name='web/security.txt', content_type='text/plain')),

    *debug_toolbar_urls(),
    path("i18n/", decorator_include(
        permission_required_else_denied('internal.is_internal'),
        'django.conf.urls.i18n'
    )),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),  # for development only; Nginx is used in production

    *ckeditor_uploader_urls(),
]
urlpatterns += logout_urls()

committee_bulletin_urlpatterns = [
    views.CommitteeBulletinBoardView.get_path('dev-board'),
    views.CommitteeBulletinBoardView.get_path('event-board'),
    views.CommitteeBulletinBoardView.get_path('mentor-board'),
    views.CommitteeBulletinBoardView.get_path('pr-board'),
]

internal_contentbox_urlpatterns = [
    path("<int:pk>/edit/", views.EditInternalContentBoxView.as_view(), name='contentbox_edit'),
]

member_urlpatterns = [
    path("members/", views.MemberListView.as_view(), name='member_list'),
    path("members/<int:pk>/", views.MemberListView.as_view(), name='member_detail'),
    path("members/create/", views.CreateMemberView.as_view(), name='create_member'),
    path("members/<int:pk>/edit/", views.EditMemberView.as_view(), name='edit_member'),
    path("members/<int:pk>/edit/status/", views.EditMemberStatusView.as_view(), name='edit_member_status'),
    path("members/<int:pk>/edit/status/quit/", views.MemberQuitView.as_view(), name='member_quit'),
    path("members/<int:pk>/edit/status/retire/", views.MemberRetireView.as_view(), name='member_retire'),
    path("members/<int:member_pk>/access/<int:pk>/edit/", views.EditSystemAccessView.as_view(), name='edit_system_access'),
]

secret_urlpatterns = [
    path("secrets/", views.SecretListView.as_view(), name='secret_list'),
    path("secrets/create/", views.CreateSecretView.as_view(), name='create_secret'),
    path("secrets/<int:pk>/edit/", views.EditSecretView.as_view(), name='edit_secret'),
    path("secrets/<int:pk>/delete/", views.DeleteSecretView.as_view(), name='delete_secret'),
]

quote_urlpatterns = [
    path("quotes/", views.QuoteListView.as_view(), name='quote_list'),
    path("quotes/add/", views.QuoteCreateView.as_view(), name='quote_create'),
    path("quotes/<int:pk>/change/", views.QuoteUpdateView.as_view(), name='quote_update'),
    path("quotes/<int:pk>/delete/", views.QuoteDeleteView.as_view(), name='quote_delete'),
]

internal_urlpatterns = [
    path("", views.HomeView.as_view(url_name='home'), name='home'),
    path("bulletins/", include(committee_bulletin_urlpatterns)),
    views.InternalDisplayContentBoxView.get_path('make-history'),
    path("contentbox/", include(internal_contentbox_urlpatterns)),

    path("", decorator_include(
        permission_required_else_denied('internal.view_member'),
        member_urlpatterns
    )),
    path("", decorator_include(
        permission_required_else_denied('internal.view_secret'),
        secret_urlpatterns
    )),
    path("", decorator_include(
        permission_required_else_denied('internal.view_quote'),
        quote_urlpatterns
    )),
]

urlpatterns += i18n_patterns(
    path("", decorator_include(
        permission_required_else_denied('internal.is_internal'),
        internal_urlpatterns
    )),

    prefix_default_language=False,
)
