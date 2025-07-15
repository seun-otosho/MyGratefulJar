from fasthtml.common import *

from themes.nemesis.components import hero_slider
from themes.nemesis.main import Base, BaseLayout
from themes.nemesis.meta import sample_posts
from .components import ContactFormComponent, homepage, contact_page


def base(request):
    page = Base(
        request,
        "Base",
        "",
        "feed",
    )
    return HttpResponse(to_xml(page), content_type="text/html")


def home(request):
    featured_post = next((post for post in sample_posts if post['is_featured']), sample_posts[0])
    page = BaseLayout(
        request,
        "Welcome",
        "",
        "feed",
        *homepage(request),
        slider=hero_slider(featured_post)
    )
    return HttpResponse(to_xml(page), content_type="text/html")


def contact_view(request):
    # if request.method == 'POST':
    #     form = ContactForm(request.POST)
    #     if form.is_valid():
    #         # Process the data (e.g., send an email)
    #         print("Form is valid!")
    #         print(form.cleaned_data)
    #         # For this demo, just show a success message
    #         page = BaseLayout(
    #             request,
    #             "Success",
    #             "",
    #             H2('Thank You!'),
    #             P('Your message has been sent.'),
    #         )
    #         return HttpResponse(to_xml(page))
    # else:
    #     form = ContactForm()  # An unbound form
    #
    # fh_form = django_form_to_fasthtml(form)

    # On GET or if form is invalid, render the form page
    page = BaseLayout(
        request,
        "Contact Us",
        "",
        "page",
        contact_page(),
    )
    return HttpResponse(to_xml(page))


def welcome(request):
    from home.pages import create_welcome_page
    html = create_welcome_page()
    return HttpResponse(html, content_type="text/html")


from django.http import HttpResponse


def item_list_view(request):
    from .components import BaseLayout, ItemListPage
    # In a real app, this data would come from your database
    # e.g., items = MyModel.objects.values_list('name', flat=True)
    sample_items = ['Apples', 'Bananas', 'Cherries']

    # Compose components: wrap the page content in the layout
    page = BaseLayout(
        ItemListPage(items=sample_items),
        title="Item List",
        request=request
    )
    return HttpResponse(to_xml(page))


def about_view(request):
    from .components import BaseLayout, AboutPage
    page = BaseLayout(
        AboutPage(),
        title="About Us",
        request=request
    )
    return HttpResponse(to_xml(page))
    # return page
