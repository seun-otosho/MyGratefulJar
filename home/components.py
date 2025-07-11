# core/components.py
from fasthtml.common import *
# This Django utility helps resolve static file paths
from django.templatetags.static import static


def BaseLayout(*children, title: str):
    return Html(
        Head(
            Title(title),
            Meta(charset="UTF-_8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            # Use Django's static() function to get the correct URL for our CSS
            Link(rel="stylesheet", href=static('css/style.css'))
        ),
        Body(
            Nav(
                A('Home', href='/items/'),
                A('About', href='/about/'),
                A('Contact', href='/contact/'),
            ),
            Main(*children) # Render child components here
        )
    )


# A component to display a list of items
def ItemListPage(items: list[str]):
    return Div(
        H2('A List of Items'),
        Ul(
            # We can use loops directly in our component definition
            *[Li(item) for item in items]
        )
    )

# A simple "About" page
def AboutPage():
    return Div(
        H2('About Us'),
        P('This is a demo project combining Django and FastHTML.')
    )

from django.middleware.csrf import get_token

# A component to render our contact form
def ContactFormComponent(form, request):
    # We need the request to generate the CSRF token
    csrf_token = get_token(request)
    return Form(
        H2('Contact Us'),
        # Manually add the CSRF token, as we aren't using {% csrf_token %}
        Input(type='hidden', name='csrfmiddlewaretoken', value=csrf_token),
        # Render the form fields. `form.as_p` generates <p>-wrapped fields.
        # `Raw` tells FastHTML to inject the HTML string directly.
        NotStr(form.as_p()),
        # Raw(form.as_p()),
        Button('Submit', type='submit')
    )
