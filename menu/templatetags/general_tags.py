from django import template

from menu.models import Menu, Font, ThemeColorScheme, FooterDetails
from home.models import SocialButton

register = template.Library()


@register.simple_tag()
def get_menu(slug):
    try:
        menu = Menu.objects.filter(slug=slug).first()
    except:
        menu = None

    return menu


@register.simple_tag()
def get_font(slug):
    try:
        font = Font.objects.filter(slug=slug).first()
    except:
        font = None

    return font


@register.simple_tag()
def get_theme(slug):
    try:
        theme = ThemeColorScheme.objects.filter(slug=slug).first()
    except:
        theme = None

    return theme


@register.simple_tag()
def get_social_buttons():
    return SocialButton.objects.all()


@register.simple_tag()
def get_footer(slug):
    try:
        footer = FooterDetails.objects.filter(slug=slug).first()
    except:
        footer = None

    return footer
