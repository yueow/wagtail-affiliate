import json

from django import forms
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.conf.urls import url
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseNotFound
from django.template.loader import render_to_string
from queryset_sequence import QuerySetSequence

from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from wagtail.core.models import Page, Orderable, ClusterableModel
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from django.core.validators import MinLengthValidator

from wagtailmetadata.models import MetadataPageMixin

from wagtail.search import index
from wagtail.search.models import Query

from home import models as home_models


class ReviewPage(Page):
    template = 'blog/review_page.html'

    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
    )

    before_description = RichTextField(blank=True, null=True)
    rating_title = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(auto_now_add=True, null=True, blank=True)

    after_title = models.CharField(max_length=100, null=True, blank=True) 
    after = RichTextField(blank=True, null=True)

    # Categories
    node = ParentalManyToManyField('home.Node', blank=True)


    def get_best_items(self):
        # best1 = self.review_items.filter.first or None
        pass

    def get_meta_image(self):
        return self.thumbnail or None
    
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

        context['read_items'] = [i.read_page for i in self.read_items.all()]
        context['best_items'] = self.review_items.filter(
            Q(premium_pick=True)|
            Q(best_value=True)|
            Q(best_choice=True))
        return context

    content_panels = Page.content_panels + [
        # FieldPanel('title'),
        ImageChooserPanel('thumbnail'),
        FieldPanel('before_description'),
        FieldPanel('rating_title'),
        FieldPanel('after_title'),
        FieldPanel('after'),

        InlinePanel('review_items', max_num=15, label="Review Items"),
        InlinePanel('read_items', max_num=3, label="Read Items"),
        FieldPanel('node', widget=forms.CheckboxSelectMultiple),
    ]


class ReviewItem(ClusterableModel, Orderable):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1024, null=True, blank=True)

    affiliate_name = models.CharField(max_length=100, blank=True, null=True)
    affiliate_link = models.URLField(blank=True, null=True)

    premium_pick = models.BooleanField(default=False)
    best_value = models.BooleanField(default=False)
    best_choice = models.BooleanField(default=False)

    page = ParentalKey(
        ReviewPage,
        on_delete=models.SET_NULL,
        related_name='review_items',
        blank=True,
        null=True,
        )

    @property
    def thumbnail(self):
        thumbnail = self.review_images.first()
        
        if thumbnail:
            return thumbnail.image
        else:
            return None


    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('description'),
        index.SearchField('affiliate_name'),

    ]

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),

        FieldPanel('affiliate_name'),
        FieldPanel('affiliate_link'),

        FieldPanel('best_value'),
        FieldPanel('best_choice'),
        FieldPanel('premium_pick'),

        InlinePanel('review_images', max_num=4, label="Gallery images"),

        InlinePanel('review_spec', max_num=7, label="Review Specification"),
        InlinePanel('review_feature', max_num=7, label="Review Key Features"),

    ]

# Review Item Specification
class ReviewSpec(Orderable):
    title = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    page = ParentalKey(ReviewItem, on_delete=models.CASCADE, related_name='review_spec')

    panels = [
        FieldPanel('title'),
        FieldPanel('value'),
    ]

# Review Item Feature
class ReviewFeature(Orderable):
    feature = models.CharField(max_length=200)

    page = ParentalKey(ReviewItem, on_delete=models.CASCADE, related_name='review_feature')

    panels = [
        FieldPanel('feature'),
    ]

# Blog Page Image Gallery
class ReviewGalleryImage(Orderable):
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)
    
    page = ParentalKey(ReviewItem, on_delete=models.CASCADE, related_name='review_images')

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]





# Read Articles
class ReviewPageRead(Orderable):
    read_page = models.ForeignKey(
        "ReviewPage",
        related_name="+",
        on_delete=models.CASCADE,
    )

    page = ParentalKey(ReviewPage, on_delete=models.CASCADE, related_name='read_items')

    panels = [
        PageChooserPanel("read_page"),
    ]


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
        InlinePanel('adv_block', max_num=1, label="Adv Side Block"),
        InlinePanel('related_items', max_num=3, label="Related Items"),
    ]


# Related Products
class BlogPageRelatedProduct(Orderable):
    related_page = models.ForeignKey(
        "BlogPage",
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


# Blog Index Page
class BlogIndexPage(MetadataPageMixin, RoutablePageMixin, Page):
    template = 'blog/category_page.html'

    @property
    def blogs(self):
        blogs = BlogPage.objects.live()
        blogs = blogs.order_by('-date')

        return blogs

    @property
    def reviews(self):
        reviews = ReviewPage.objects.all()
        reviews = reviews.order_by('-date')

        return reviews

    @property
    def categories(self):
        categories = home_models.Node.objects.get(pk=1).get_children()
        return categories

    #def get_context(self, request):
    #    context = super(BlogIndexPage, self).get_context(request)
#	context['categories'] = self.categories
        # search_query = request.GET.get('q', None)
        # if search_query:
        #     context['blogs'] = BlogPage.objects.search(search_query, fields=['title','body'])
        #     context['search_term'] = search_query
        #     context['search_type'] = 'search'
        #     return context


        # allblogs = self.blogs
        # # categories 

        # page = request.GET.get('page')
        # paginator = Paginator(allblogs, 6)

        # try:
        #     blogs = paginator.page(page)
        # except PageNotAnInteger:
        #     blogs = paginator.page(1)
        # except EmptyPage:
        #     blogs = paginator.page(paginator.num_pages)
    

        # context['blogs'] = blogs

        return context

    @route(r'^$', name='all_categories')
    def all_categories(self, request):
        context = super(BlogIndexPage, self).get_context(request)
        context['categories'] = home_models.Node.objects.get(pk=1).get_children()

        search_query = request.GET.get('q', None)
        if search_query:
            context['blogs'] = BlogPage.objects.search(search_query, fields=['title','body'])
            context['search_term'] = search_query
            context['search_type'] = 'search'
            return render(request, 'blog/category_page.html', context)


        allblogs = QuerySetSequence(self.blogs, self.reviews)

        page = request.GET.get('page')
        paginator = Paginator(allblogs, 6)

        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)
    

        context['blogs'] = blogs

        return render(request, 'blog/category_page.html', context)

    # Ajax Filtering
    @route('filtering_ajax/', name='filtering_ajax')
    def filtering_ajax(self, request, *args, **kwargs):
        if request.is_ajax():
            form_data = json.loads(request.GET.get('form_data'))
            # print(form_data)

            # Deserialization JSON object
            form_data = { key:value for (key, value) in [o.values() for o in form_data] }
            # print(form_data)

            # Categories(All, Fitness....)
            if 'categories-input' in form_data and form_data['categories-input'] != 'all':
                cat = home_models.Node.objects.get(pk=form_data['categories-input'])
                blogs = cat.blogpage_set.all()
                reviews = cat.reviewpage_set.all()
            else:
                blogs = self.blogs
                reviews = self.reviews
            
            # Post Type(All, Product, Review)
            if 'post-input' in form_data and form_data['post-input'] != 'all':
                if form_data['post-input'] == 'product':
                    result = blogs
                elif form_data['post-input'] == 'review':
                    result = reviews
            else:
                result = QuerySetSequence(blogs, reviews)

            #  checking
            # if 'license' in parsed_JSON:
            #     blogs = result_queryset.filter(cls._FILTER_LIST['license'])


            # Sorting. Sorting gotta occurs after all filters in the order
            # blogs = result_queryset.order_by(cls._FILTER_LIST['sorting'][parsed_JSON['sorting']])

            # context = super(BlogIndexPage, self).get_context(request)

            data = {}
            data['html_from_view'] = render_to_string(
                template_name="blog/includes/cards.html", 
                context={
                    'blogs': result,

            })
            return JsonResponse(data=data)
        return JsonResponse({'result': None})

    # Categories
    @route(r"^(?P<cat_slug>[-\w]*)/$", name='category_view')
    def category(self, request, cat_slug):
        context = super(BlogIndexPage, self).get_context(request)
        result = None

        try:
            cat = home_models.Node.objects.get(name__iexact=cat_slug)
            blogs = cat.blogpage_set.all()
            reviews = cat.reviewpage_set.all()
            result = QuerySetSequence(blogs, reviews)
        except:
            return HttpResponseRedirect('/')

        # page = request.GET.get('page')
        # paginator = Paginator(blogs, 6)

        # try:
        #     paginated_blogs = paginator.page(page)
        # except PageNotAnInteger:
        #     paginated_blogs = paginator.page(1)
        # except EmptyPage:
        #     paginated_blogs = paginator.page(paginator.num_pages)
    
        context['blogs'] = result
        context['filter_term'] = cat_slug.capitalize()

        return render(request, 'blog/category_page.html', context)

# Advertise Block
class AdvBlock(Orderable):
    title = models.CharField(blank=True, null=True, max_length=100)
    # description = models.CharField(blank=True, null=True, max_length=250)
    
    related_page = models.ForeignKey(
        "BlogPage",
        related_name="+",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    link = models.URLField(blank=True, null=True)

    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+',
        blank=True,
        null=True,
    )
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='adv_block')

    panels = [
        FieldPanel('title'),
        # FieldPanel('description'),
        ImageChooserPanel('image'),
        PageChooserPanel("related_page"),
    ]