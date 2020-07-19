import json

from django import forms
from django.db import models
from django.conf.urls import url
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string


from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from django.core.validators import MinLengthValidator

from wagtailmetadata.models import MetadataPageMixin

from wagtail.search import index
from wagtail.search.models import Query

from home import models as home_models


# Blog/Product Page Entity
class BlogPage(MetadataPageMixin, Page):
    date = models.DateField("Post date")
    # intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)

    # Categories
    node = ParentalManyToManyField('home.Node', blank=True)

    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    weight = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)


    # Links
    affiliate_name = models.CharField(max_length=100, blank=True, null=True)
    affiliate_link = models.URLField(blank=True, null=True)
    
    # Social links
    facebook_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    pinterest_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    
    # Method returns first element of the image gallery
    @property
    def main_image(self):
        gallery_item = self.gallery_images.first()
        
        if gallery_item:
            return gallery_item.image
        else:
            return None
    
    @property    
    def categories(self):
        categories = self.node.all()
        return categories

    @property
    def main_category(self):
        categories = self.categories
        if categories:
            category = categories.first()
        else:
            category = None
        return category


    def get_context(self, request):
        context = super().get_context(request)
        context['related_items'] = [i.related_page for i in self.related_items.all()]

        return context

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('brand'),
        index.SearchField('model'),
        index.SearchField('color'),
        index.SearchField('affiliate_name'),

        index.SearchField('node'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        # ImageChooserPanel('main_image'),
        # FieldPanel('intro'),

        FieldPanel('body'),
        FieldPanel('brand'),
        FieldPanel('model'),
        FieldPanel('weight'),
        FieldPanel('color'),
        FieldPanel('dimensions'),
        FieldPanel('affiliate_name'),
        FieldPanel('affiliate_link'),
        FieldPanel('facebook_link'),
        FieldPanel('twitter_link'),
        FieldPanel('pinterest_link'),
        FieldPanel('youtube_link'),
        FieldPanel('instagram_link'),
        InlinePanel('gallery_images', max_num=6, label="Gallery images"),
        FieldPanel('node', widget=forms.CheckboxSelectMultiple),
        InlinePanel('related_items', max_num=3, label="Related Items"),
    ]


# Related Products
class BlogPageRelatedProduct(Orderable):
    related_page = models.ForeignKey(
        "BlogPage",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )

    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='related_items')

    panels = [
        PageChooserPanel("related_page"),
    ]

    

# Blog Page Image Gallery
class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


# 
class BlogIndexPage(MetadataPageMixin, RoutablePageMixin, Page):
    template = 'blog/category_page.html'


    # Ajax Filtering
    @route('filtering_ajax/')
    def filtering_ajax(self, request, *args, **kwargs):
        if request.is_ajax():
            form_data = json.loads(request.GET.get('form_data'))
            print(form_data)
            # Deserialization JSON object
            form_data = { key:value for (key, value) in [o.values() for o in form_data] }
            print(form_data)

            # Categories 
            if 'categories-input' in form_data and form_data['categories-input'] != 'all':
                cat = home_models.Node.objects.get(pk=form_data['categories-input'])
                blogs = cat.blogpage_set.all()
            else:
                blogs = self.blogs

            # !Post Type

            #  checking
            # if 'license' in parsed_JSON:
            #     blogs = result_queryset.filter(cls._FILTER_LIST['license'])

            data = {}

            # Sorting. Sorting gotta occurs after all filters in the order
            # blogs = result_queryset.order_by(cls._FILTER_LIST['sorting'][parsed_JSON['sorting']])

        #  context = super(BlogIndexPage, self).get_context(request)

            data['html_from_view'] = render_to_string(
                template_name="blog/includes/cards.html", 
                context={
                    'blogs': blogs,

            })
            return JsonResponse(data=data)
        return JsonResponse({'result': None})

    @property
    def blogs(self):
        # Получить список страниц блога, которые являются потомками этой страницы
        blogs = BlogPage.objects.live()

        # Сортировать по дате
        blogs = blogs.order_by('-date')

        return blogs

    @property
    def categories(self):
        categories = home_models.Node.objects.get(pk=1).get_children() or None
        return categories

    def get_context(self, request):
        context = super(BlogIndexPage, self).get_context(request)

        search_query = request.GET.get('q', None)
        if search_query:
            context['blogs'] = BlogPage.objects.search(search_query, fields=['title','body'])
            context['search_term'] = search_query
            context['search_type'] = 'search'
            return context


        allblogs = self.blogs
        # categories 

        page = request.GET.get('page')
        paginator = Paginator(allblogs, 6)

        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)
    

        context['blogs'] = blogs

        return context