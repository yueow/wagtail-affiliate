from django import forms
from django.db import models
from django.conf.urls import url
from django.shortcuts import get_object_or_404
from django.contrib.admin.utils import quote, unquote
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import PermissionDenied

from modelcluster.fields import ParentalKey
from wagtail.core.models import Page, Orderable
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel

from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import CreateView
from wagtail.search import index
from django.template.loader import render_to_string

from wagtailmetadata.models import MetadataPageMixin

from treebeard.mp_tree import MP_Node
from blog.models import BlogPage


node_name_validator = RegexValidator(
    regex='^[\w][a-zA-Z &]+$',
    message="Letters, numbers and '&' only plus must start with a letter.",
)


class Node(index.Indexed, MP_Node):
    """Represents a single nestable Node in the corporate taxonomy."""

    # node editable fields
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text='Keep the name short, ideally one word.',
        validators=[node_name_validator, MinLengthValidator(3)]
    )
    # depth = models.PositiveIntegerField(null=True)
    aliases = models.TextField(
        'Also known as',
        max_length=255,
        blank=True,
        help_text="What else is this known as or referred to as?"
    )

    # node tree specific fields and attributes
    node_order_index = models.IntegerField(
        blank=True,
        default=0,
        editable=False
    )
    node_child_verbose_name = 'child'
    node_order_by = ['node_order_index', 'name']

    panels = [
        FieldPanel('name'),
        # FieldPanel('parent'),  # virtual field - see TopicForm
        FieldPanel('aliases', widget=forms.Textarea(attrs={'rows': '5'})),
    ]

    def get_as_listing_header(self):
        """Build HTML representation of node with title & depth indication."""
        depth = self.get_depth()
        rendered = render_to_string(
            'includes/node_list_header.html',
            {
                'depth': depth,
                'depth_minus_1': depth - 1,
                'is_root': self.is_root(),
                'name': self.name,
            }
        )
        return rendered
    get_as_listing_header.short_description = 'Name'
    get_as_listing_header.admin_order_field = 'name'

    def get_parent(self, *args, **kwargs):
        """Duplicate of get_parent from treebeard API."""
        return super().get_parent(*args, **kwargs)
    get_parent.short_description = 'Parent'

    search_fields = [
        index.SearchField('name', partial_match=True),
        index.SearchField('aliases', partial_match=False, boost=0.25),
    ]

    def delete(self):
        """Prevent users from deleting the root node."""
        if self.is_root():
            raise PermissionDenied('Cannot delete root Topic.')
        else:
            super().delete()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'



class NodeButtonHelper(ButtonHelper):
    """Custom button functionality for node listing buttons."""

    def prepare_classnames(self, start=None, add=None, exclude=None):
        """Parse classname sets into final css classess list."""
        classnames = start or []
        classnames.extend(add or [])
        return self.finalise_classname(classnames, exclude or [])

    def delete_button(self, pk, *args, **kwargs):
        """Ensure that the delete button is not shown for root node."""
        instance = self.model.objects.get(pk=pk)
        if instance.is_root():
            return
        return super().delete_button(pk, *args, **kwargs)

    def inspect_button(self, *args, **kwargs):
        """Replace the term 'Inspect' with 'Details' in listing buttons."""
        button = super().inspect_button(*args, **kwargs)
        button['label'] = button['label'].replace('Inspect', 'Details')
        button['title'] = button['label'].replace('Inspect', 'Details', 1)
        return button

    def add_child_button(self, pk, child_verbose_name, **kwargs):
        """Build a add child button, to easily add a child under node."""
        classnames = self.prepare_classnames(
            start=self.edit_button_classnames + ['icon', 'icon-plus'],
            add=kwargs.get('classnames_add'),
            exclude=kwargs.get('classnames_exclude')
        )
        return {
            'classname': classnames,
            'label': 'Add %s %s' % (
                child_verbose_name, self.verbose_name),
            'title': 'Add %s %s under this one' % (
                child_verbose_name, self.verbose_name),
            'url': self.url_helper.get_action_url('add_child', quote(pk)),
        }

    def get_buttons_for_obj(self, obj, exclude=None, *args, **kwargs):
        """Override the getting of buttons, prepending create child button."""
        buttons = super().get_buttons_for_obj(obj, *args, **kwargs)

        add_child_button = self.add_child_button(
            pk=getattr(obj, self.opts.pk.attname),
            child_verbose_name=getattr(obj, 'node_child_verbose_name'),
            **kwargs
        )
        buttons.append(add_child_button)

        return buttons


class AddChildNodeViewClass(CreateView):
    """View class that can take an additional URL param for parent id."""

    parent_pk = None
    parent_instance = None

    def __init__(self, model_admin, parent_pk):
        self.parent_pk = unquote(parent_pk)
        object_qs = model_admin.model._default_manager.get_queryset()
        object_qs = object_qs.filter(pk=self.parent_pk)
        self.parent_instance = get_object_or_404(object_qs)
        super().__init__(model_admin)

    def get_page_title(self):
        """Generate a title that explains you are adding a child."""
        title = super().get_page_title()
        return title + ' %s %s for %s' % (
            self.model.node_child_verbose_name,
            self.opts.verbose_name,
            self.parent_instance
        )

    def get_initial(self):
        """Set the selected parent field to the parent_pk."""
        return {'parent': self.parent_pk}

# Forms
class BasicNodeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        depth_line = '-' * (obj.get_depth() - 1)
        return "{} {}".format(depth_line, super().label_from_instance(obj))


class NodeForm(WagtailAdminModelForm):

    parent = BasicNodeChoiceField(
        required=True,
        queryset=Node.objects.all(),
        empty_label=None,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs['instance']

        if instance.is_root() or Node.objects.count() == 0:
            # hide and disable the parent field
            self.fields['parent'].disabled = True
            self.fields['parent'].required = False
            self.fields['parent'].empty_label = 'N/A - Root Node'
            self.fields['parent'].widget = forms.HiddenInput()

            # update label to indicate this is the root
            self.fields['name'].label += ' (Root)'
        elif instance.id:
            self.fields['parent'].initial = instance.get_parent()

    def save(self, commit=True, *args, **kwargs):
        instance = super().save(commit=False, *args, **kwargs)
        parent = self.cleaned_data['parent']

        if not commit:
            # simply return the instance if not actually saving (committing)
            return instance

        if instance.id is None:  # creating a new node
            if Node.objects.all().count() == 0:  # no nodes, creating root
                Node.add_root(instance=instance)  # add a NEW root node
            else:  # nodes exist, must be adding node under a parent
                instance = parent.add_child(instance=instance)
        else:  # editing an existing node
            instance.save()  # update existing node
            if instance.get_parent() != parent:
                instance.move(parent, pos='sorted-child')
        return instance


Node.base_form_class = NodeForm


# Home Page Model
class HomePage(MetadataPageMixin, Page):
    template = 'home/home_page.html'

    # title = models.CharField(max_length=120, blank=True, null=True)
    # intro = RichTextField(blank=True, null=True)
 
    def get_context(self, request):
        # Обновляем контекст для внесения только опубликованных постов в обратном хронологическом порядке
        context = super().get_context(request)
        featured_posts = BlogPage.objects.all()[:6]
        latest_posts = BlogPage.objects.all()[:6]
        context['featured_posts'] = featured_posts
        context['latest_posts'] = latest_posts

        # context['bsp_item'] = 

        return context
    
    content_panels = Page.content_panels + [
        FieldPanel('title'),
        InlinePanel('slider_items', max_num=3, label="Slider"),
        InlinePanel('social_buttons', max_num=5, label="Social Buttons"),
        InlinePanel('bsp_item', max_num=1,  label="Best Selling Product"),
    ]


# Social Buttons Model
class SocialButton(Orderable):
    name = models.CharField(max_length=100)
    link = models.URLField()
    icon_class = models.CharField(max_length=100)

    page = ParentalKey('HomePage', related_name='social_buttons')

    def __str__(self):
        return f'{self.name} - {self.link}'


# Home Page Slider Carousel Model
class SliderItem(Orderable):
    title = models.CharField(max_length=200, blank=True, null=True)
    page = ParentalKey('HomePage', related_name='slider_items')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    cat = models.CharField(max_length=120)
    link = models.URLField()

    panels = [
        FieldPanel('title'),
        ImageChooserPanel('image'),
        FieldPanel('cat'),
        FieldPanel('link'),
    ]


# Best Selling Product Model
class BSPItem(Orderable):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=512)
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )

    button_link = models.URLField(blank=True, null=True)
    page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    
    parental_page = ParentalKey('HomePage', on_delete=models.CASCADE, related_name='bsp_item')

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        ImageChooserPanel('image'),
        FieldPanel('button_link'),
        PageChooserPanel("page"),
    ]
