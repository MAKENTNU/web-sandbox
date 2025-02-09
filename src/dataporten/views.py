from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.utils.http import urlencode
from django.views import View
from social_django import views as social_views
from social_django.models import UserSocialAuth

from users.models import User
from util.logging_utils import log_request_exception
from . import ldap_utils

# Assign these functions to module-level variables, to facilitate testing (through monkey patching)
complete = social_views.complete
get_user_details_from_email = ldap_utils.get_user_details_from_email


class Logout(View):

    def post(self, request):
        user: User = request.user
        logout(request)

        try:
            id_token = user.social_auth.first().extra_data['id_token']
        except (AttributeError, UserSocialAuth.DoesNotExist, KeyError):
            return HttpResponseRedirect(settings.DATAPORTEN_LOGOUT_URL)

        # See https://docs.feide.no/service_providers/manage/openid_connect/redir_etter_logout.html
        url_parameter_string = urlencode({
            # NOTE: This can be either the Norwegian or the English URL depending on the user visiting, so both of those URLs must be registered
            # as allowed "Redirect URI[s] for logout" in the OpenID Connect configuration in Feide's customer portal!
            'post_logout_redirect_uri': request.build_absolute_uri(settings.LOGOUT_REDIRECT_URL),
            'id_token_hint': id_token,
        })
        return HttpResponseRedirect(f"{settings.DATAPORTEN_LOGOUT_URL}?{url_parameter_string}")


def login_wrapper(request, backend, *args, **kwargs):
    """
    Handles the callback from the social django login. Updating the full name of the user, and possibly their username.
    Usernames are found in NTNUs LDAP server using the email to search. For some reason, some users do not have their
    email in the NTNU LDAP system. For these users we derive their username from the local part of their email. This
    will be the correct NTNU username for all students. We have yet to find an employee without their email in LDAP.

    :return: The landing page after login, as defined by the social django configuration.
    """
    try:
        response = complete(request, backend, *args, **kwargs)
    except Exception as e:
        raise RuntimeError("Authentication through Dataporten failed.") from e

    user: User = request.user
    social_data = user.social_auth.first().extra_data

    # If any of the user's names have not been set...
    if (not user.get_full_name() or not user.ldap_full_name
            # ...or if the user has not set a different name after account creation:
            or user.get_full_name().strip() == user.ldap_full_name.strip()):
        _update_full_name_if_different(user, social_data)
    # Update the LDAP name after the full name has (potentially) been set.
    # This is only important if the user has not logged in before, as the full name has not yet been set.
    _update_ldap_full_name_if_different(user, social_data)

    try:
        # Try to retrieve username from NTNUs LDAP server. Otherwise use the first part of the email as the username
        ldap_data = get_user_details_from_email(user.email, use_cached=False)
    except Exception as e:
        log_request_exception("Looking up user details through LDAP failed.", e, request)
        ldap_data = {}
    _update_username_if_different(user, social_data, ldap_data)

    return response


def _update_full_name_if_different(user: User, social_data: dict):
    split_ldap_name = social_data['fullname'].split()
    if not split_ldap_name:
        return
    old_full_name = user.get_full_name()
    user.first_name = " ".join(split_ldap_name[:-1])
    user.last_name = split_ldap_name[-1]
    if user.get_full_name() != old_full_name:
        user.save()


def _update_ldap_full_name_if_different(user: User, social_data: dict):
    potentially_new_ldap_full_name = social_data['fullname']
    if not potentially_new_ldap_full_name:
        return
    if user.ldap_full_name != potentially_new_ldap_full_name:
        user.ldap_full_name = potentially_new_ldap_full_name
        user.save()


def _update_username_if_different(user: User, social_data: dict, ldap_data: dict):
    potentially_new_username = (
            social_data.get('username')
            or ldap_data.get('username')
            or user.email.split("@")[0]
    )
    if not potentially_new_username:
        return
    if user.username != potentially_new_username:
        user.username = potentially_new_username
        user.save()
