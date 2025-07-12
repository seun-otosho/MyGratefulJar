from fasthtml.common import *

from home.pages import create_welcome_page
from themes.nemesis.main import homepage


def home(request):

    return HttpResponse(to_xml(homepage(request)), content_type="text/html")


def welcome(request):
    html = create_welcome_page()
    return HttpResponse(html, content_type="text/html")

from django.http import HttpResponse
from .components import BaseLayout, ItemListPage, AboutPage

def item_list_view(request):
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
    page = BaseLayout(
        AboutPage(),
        title="About Us",
        request=request
    )
    return HttpResponse(to_xml(page))
    # return page

# core/views.py
from django.shortcuts import render # We can still use render for simplicity if needed
from .forms import ContactForm
from .components import BaseLayout, ContactFormComponent

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the data (e.g., send an email)
            print("Form is valid!")
            print(form.cleaned_data)
            # For this demo, just show a success message
            page = BaseLayout(
                H2('Thank You!'),
                P('Your message has been sent.'),
                title="Success"
            )
            return HttpResponse(to_xml(page))
    else:
        form = ContactForm() # An unbound form

    # On GET or if form is invalid, render the form page
    page = BaseLayout(
        ContactFormComponent(form=form, request=request),
        title="Contact Us",
        request=request
    )
    return HttpResponse(to_xml(page))
