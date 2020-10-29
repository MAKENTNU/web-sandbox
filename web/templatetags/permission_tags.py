from django import template
from django.contrib.auth.models import Permission

register = template.Library()


@register.filter(name='has_any_permissions')
def has_any_permissions(user):
    for group in user.groups.all():
        if Permission.objects.filter(group=group).exists():
            return True
    return Permission.objects.filter(user=user).exists()


@register.filter(name="has_any_article_permission")
def has_any_article_permission(user):
    return any(user.has_perm(f"news.{action}_article") for action in ["add", "change", "delete"])


@register.filter(name="has_any_event_permission")
def has_any_event_permission(user):
    models = "event", "timeplace"
    actions = "add", "change", "delete"
    for model in models:
        for action in actions:
            if user.has_perm(f"news.{action}_{model}"):
                return True
    return False


@register.filter(name="has_any_makerspace_permission")
def has_any_makerspace_permission(user):
    return any(user.has_perm(f"makerspace.{action}_makerspace") for action in ["add", "change", "delete"])


@register.filter
def has_any_equipment_permissions(user):
    return any(user.has_perm(f"makerspace.{action}_equipment") for action in ["add", "change", "delete"])


@register.filter
def has_any_faq_permissions(user):
    return user.has_perm("can_add_questions")
