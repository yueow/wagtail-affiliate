
from wagtail.contrib.modeladmin.options import ModelAdmin
from home.models import Node

class NodeAdmin(ModelAdmin):
    """Class for presenting topics in admin using modeladmin."""

    model = Node

    # admin menu options
    menu_icon = 'fa-cube'  # using wagtail-fontawesome
    menu_order = 800

    # listing view options
    list_per_page = 50
    # list_display = ('name', 'get_parent', 'aliases')
    search_fields = ('name', 'aliases')

    # inspect view options
    inspect_view_enabled = True
    inspect_view_fields = ('name', 'get_parent', 'aliases', 'id')

    list_display = ('get_as_listing_header', 'get_parent', 'aliases')