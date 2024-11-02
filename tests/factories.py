import factory

from factory.django import DjangoModelFactory
from wagtail.models import Page
from wagtail.test.testapp.models import BlogCategory


class PageFactory(DjangoModelFactory):
    class Meta:
        abstract = True

    # override the _create method,
    # to establish parent-child relationship between pages
    @classmethod
    def _create(cls, model_class, *args, **kwargs):

        try:
            parent = kwargs.pop('parent')
        except KeyError:
            # no parent, appending page to root
            parent = Page.get_first_root_node()

        page = model_class(*args, **kwargs)
        parent.add_child(instance=page)

        return page

from home.models import HomePage


class HomePageFactory(PageFactory):
    class Meta:
        model = HomePage

    title = factory.Sequence(lambda n: 'Home page {0}'.format(n))



class BlogCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BlogCategory

    name = factory.Faker('word')
    icon = factory.django.ImageField(from_path=get_test_image_file())


class BlogPageFactory(PageFactory):
    class Meta:
        model = BlogPage

    title = factory.Faker('sentence')
    intro = factory.Faker('text', max_nb_chars=250)
    body = factory.Faker('paragraph')
    date = factory.Faker('date_this_century')
    categories = factory.SubFactory(BlogCategoryFactory)
    image = factory.django.ImageField(from_path=get_test_image_file())


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    page = factory.SubFactory(BlogPageFactory)
    author = factory.Faker('name')
    email = factory.Faker('email')
    content = factory.Faker('paragraph')
    created_date = factory.Faker('date_time_this_decade')
    approved = factory.Faker('boolean')
    parent = None

