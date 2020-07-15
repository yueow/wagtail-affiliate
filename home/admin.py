from django.conf.urls import url
from wagtail.contrib.modeladmin.options import ModelAdmin
from home.models import Node, NodeButtonHelper

class NodeAdmin(ModelAdmin):
    """Class for presenting topics in admin using modeladmin."""

    model = Node

    # admin menu options
    menu_icon = 'fa-cube'  # using wagtail fontawesome
    menu_order = 800

    # listing view options
    list_display = ('get_as_listing_header', 'get_parent', 'aliases')
    list_per_page = 50
    search_fields = ('name', 'aliases')

    # inspect view options
    inspect_view_enabled = True
    inspect_view_fields = ('name', 'get_parent', 'aliases', 'id')

    # other overrides
    button_helper_class = NodeButtonHelper

    def add_child_view(self, request, instance_pk):
        """Generate a class-based view to provide 'add child' functionality."""
        # instance_pk will become the default selected parent_pk
        kwargs = {'model_admin': self, 'parent_pk': instance_pk}
        view_class = AddChildNodeViewClass
        return view_class.as_view(**kwargs)(request)

    def get_admin_urls_for_registration(self):
        """Add the new url for add child page to the registered URLs."""
        urls = super().get_admin_urls_for_registration()
        add_child_url = url(
            self.url_helper.get_action_url_pattern('add_child'),
            self.add_child_view,
            name=self.url_helper.get_action_url_name('add_child')
        )
        return urls + (add_child_url, )