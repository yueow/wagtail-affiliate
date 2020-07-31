from django.db import models
from django.shortcuts import get_object_or_404, redirect

from django_extensions.db.fields import AutoSlugField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.core.models import Orderable
# from wagtail.images.models import Image
from wagtail.admin.edit_handlers import MultiFieldPanel,InlinePanel,FieldPanel,PageChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel

from wagtail.snippets.models import register_snippet

# from fontfield.fields import FontField
from colorfield.fields import ColorField



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
        
        InlinePanel('menu_item_header',  max_num=1, label="Menu Dropdown Header"),
        InlinePanel('menu_item_content', max_num=5, label="Menu Dropdown Content"),
        InlinePanel('menu_footer',  max_num=1, label="Menu Dropdown Footer"),

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

        InlinePanel('menu_footer_items',  max_num=4, label="Menu Footer Items"),
    ]


class MenuItemFooterItem(Orderable):
    footer_item_title = models.CharField(max_length=50, blank=True, null=True)
    footer_title_link = models.URLField(blank=True, null=True)

    footer_menu = ParentalKey("MenuItemFooter", related_name="menu_footer_items")
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
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


@register_snippet
class Font(ClusterableModel):
    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="title", editable=True)

    import_rule = models.CharField(max_length=1024, blank=True, null=True)
    css_rule = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return f'{self.title}'


@register_snippet
class ThemeColorScheme(ClusterableModel):
    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="title", editable=True)

    navbar_bg_color = ColorField(default='white')
    navbar_text_color = ColorField(default='#FF0000')

    brand_text_color = ColorField(default='black')

    # Subnav
    subnav_bg_color = ColorField(default='white')
    subnav_text_color = ColorField(default='black')

    # Megamenu
    megamenu_bg_color = ColorField(default='#FF0000')
    megamenu_text_color = ColorField(default='black')
    megamenu_text_hover_color = ColorField(default='#4693aa')

    # Megamenu Footer
    megamenu_footer_bg_color = ColorField(default='#4693aa')
    megamenu_footer_text_color = ColorField(default='black')

    # Theme
    theme_color = ColorField(default='#4693aa')

    # Body
    body_bg_color_primary = ColorField(default='#FF0000')
    body_bg_color_secondary = ColorField(default='#FF0000')

    # BSP
    bsp_bg_color = ColorField(default='#4693aa')
    bsp_text_color = ColorField(default='white')

    # Footer
    footer_bg_color = ColorField(default='black')
    footer_text_color = ColorField(default='white')

    # Advertise Block
    advertise_block_text_color = ColorField(default='white')

    # All categories
    categories_bg_color = ColorField(default='black')

    def __str__(self):
        return f'{self.title}'


@register_snippet
class FooterDetails(ClusterableModel):
    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="title", editable=True)

    description = models.TextField(max_length=512)
    basement = models.CharField(max_length=200) 
    
    panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        FieldPanel('description'),
        FieldPanel('basement'),
        InlinePanel("contacts", label="Contacts"),

        InlinePanel("footer_columns", max_num=5, label="Footer Columns"),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Footer Details"


# Footer Column
class FooterColumn(ClusterableModel, Orderable):
    title = models.CharField(blank=True, null=True, max_length=50)
    link_url = models.CharField(max_length=500, blank=True)

    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    open_in_new_tab = models.BooleanField(default=False, blank=True)
    page = ParentalKey("FooterDetails", related_name="footer_columns")

    panels = [
        FieldPanel("title"),
        FieldPanel("link_url"),
        PageChooserPanel("link_page"),
        FieldPanel("open_in_new_tab"),
        
        InlinePanel("footer_rows", max_num=10, label="Footer Rows"),
    ]

    def __str__(self):
        return self.title

# Footer Column Row
class FooterColumnRow(Orderable):
    title = models.CharField(
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
    page = ParentalKey("FooterColumn", related_name="footer_rows")

    panels = [
        FieldPanel("title"),
        FieldPanel("link_url"),
        PageChooserPanel("link_page"),
        FieldPanel("open_in_new_tab"),
    ] 
    
    def __str__(self):
        return self.title


# Contacts
class ContactItem(Orderable):
    contact = models.CharField(max_length=120)
    footer_menu = ParentalKey("FooterDetails", related_name="contacts")

    panels = [
        FieldPanel('contact'),
    ]

    def __str__(self):
        return self.contact


@register_snippet
class SubscriptionEmail(ClusterableModel):
    email = models.EmailField(unique=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


# View for email subscriprion
def subscribe_email(request):
    if request.method == "POST":
        email = request.POST.get('subscribe_email', None)
        try:
            SubscriptionEmail.objects.create(email=email)
        except:
            return redirect('/')            
    return redirect('/')
