from django.db import models

from django_extensions.db.fields import AutoSlugField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.images.models import Image
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import MultiFieldPanel,InlinePanel,FieldPanel,PageChooserPanel

from wagtail.core.models import Orderable
from wagtail.snippets.models import register_snippet


class MenuItem(ClusterableModel, Orderable):

    link_title = models.CharField(
        blank=True,
        null=True,
        max_length=50
    )
    link_url = models.CharField(
        max_length=500,
        blank=True
    )
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    open_in_new_tab = models.BooleanField(default=False, blank=True)
    dropdown = models.BooleanField(default=False, blank=True, verbose_name="Does it has SubMenu/Dropdown?")

    page = ParentalKey("Menu", related_name="menu_items")

    panels = [
        FieldPanel("link_title"),
        FieldPanel("link_url"),
        FieldPanel("open_in_new_tab"),
        FieldPanel("dropdown"),
        PageChooserPanel("link_page"),
        
        InlinePanel('menu_item_header', label="Menu Dropdown Header"),
        InlinePanel('menu_item_content', label="Menu Dropdown Content"),
        InlinePanel('menu_footer', label="Menu Dropdown Footer"),

    ]

    @property
    def has_header(self):
        if self.menu_item_header.count() != 0:
            return True
        return False

    @property
    def has_content(self):
        if self.menu_item_content.count() != 0:
            return True
        return False

    @property
    def has_footer(self):
        if self.menu_footer.count() != 0:
            return True
        return False

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_url:
            return self.link_url
        return '#'

    @property
    def title(self):
        if self.link_page and not self.link_title:
            return self.link_page.title
        elif self.link_title:
            return self.link_title
        return 'Missing Title'



class MenuItemHeader(Orderable):
    header_title = models.CharField(max_length=50)
    header_menu_item = ParentalKey("MenuItem", related_name="menu_item_header")

    panels = [
        FieldPanel('header_title'),
    ]


class MenuItemContentColumn(ClusterableModel, Orderable):
    column_title = models.CharField(max_length=50, blank=True, null=True) 
    column_link = models.URLField(blank=True, null=True)

    menu_item = ParentalKey("MenuItem", related_name="menu_item_content")

    panels = [
        FieldPanel('column_title'),
        FieldPanel('column_link'),

        InlinePanel('column_row', label="Content Column Item"),
    ]


class MenuItemContentRow(Orderable):
    row_title = models.CharField(max_length=50) 
    row_link = models.URLField(blank=True, null=True)

    row_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )

    menu_item = ParentalKey("MenuItemContentColumn", related_name="column_row")

    panels = [
        FieldPanel('row_title'),
        FieldPanel('row_link'),
        PageChooserPanel("row_page"),

    ]

class MenuItemFooter(ClusterableModel, Orderable):
    footer_title = models.CharField(max_length=50, blank=True, null=True)
    footer_title_link = models.URLField(blank=True, null=True)

    footer_menu = ParentalKey("MenuItem", related_name="menu_footer")

    panels = [
        FieldPanel('footer_title'),
        FieldPanel('footer_title_link'),

        InlinePanel('menu_footer_items', label="Menu Footer Items"),
    ]


class MenuItemFooterItem(Orderable):
    footer_item_title = models.CharField(max_length=50, blank=True, null=True)
    footer_title_link = models.URLField(blank=True, null=True)

    footer_menu = ParentalKey("MenuItemFooter", related_name="menu_footer_items")
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('footer_item_title'),
        FieldPanel('footer_title_link'),
        ImageChooserPanel('image'),
    ]




@register_snippet
class Menu(ClusterableModel):
    """The main menu clusterable model."""

    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="title", editable=True)
    # slug = models.SlugField()

    panels = [
        MultiFieldPanel([
            FieldPanel("title"),
            FieldPanel("slug"),
        ], heading="Menu"),
        InlinePanel("menu_items", label="Menu Item")
    ]

    def __str__(self):
        return self.title