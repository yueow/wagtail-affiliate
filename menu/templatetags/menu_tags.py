"""menus/templatetags/menus_tags.py"""
from django import template

from menu.models import Menu

register = template.Library()


@register.simple_tag()
def get_menu(slug):
    return Menu.objects.filter(slug=slug).first()