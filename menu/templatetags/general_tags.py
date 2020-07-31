from django import template

from menu.models import Menu, Font, ThemeColorScheme, FooterDetails
from home.models import SocialButton, AdvBlock, HomePage

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


@register.simple_tag()
def get_adv():
    try:
        adv = AdvBlock.objects.all().first()
    except:
        adv = None

    return adv


@register.simple_tag()
def get_social_buttons():
    links = {}
    try:
        home_page = HomePage.objects.all().first()
        if home_page.facebook_link: links['facebook_link'] = home_page.facebook_link
        if home_page.youtube_link: links['youtube_link'] = home_page.facebook_link
        if home_page.twitter_link: links['twitter_link'] = home_page.facebook_link
        if home_page.pinterest_link: links['pinterest_link'] = home_page.facebook_link
        if home_page.instagram_link: links['instagram_link'] = home_page.facebook_link
    except:
        links = {}
    return links

@register.simple_tag()
def get_logo():
    try:
        home_page = HomePage.objects.all().first()
        logo = home_page.logo
    except:
        logo = None
    return logo 
     