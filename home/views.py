from django.http import HttpResponse

from home.pages import create_welcome_page


def hello_world(request):
    html = "<html><body>Hello, world!</body></html>"
    return HttpResponse(html, content_type="text/html")


def welcome(request):
    html = create_welcome_page()
    return HttpResponse(html, content_type="text/html")