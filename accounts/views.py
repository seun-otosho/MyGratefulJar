# core/auth_views.py
from allauth.account.views import LoginView, SignupView
from django.http import HttpResponse
# from fastcore.xml import to_xml
from fasthtml.common import *

from home.components import BaseLayout
# Import our components and layout
# from config.components import BaseLayout
from .components import LoginPageComponent, SignupPageComponent


# A custom view that subclasses Allauth's LoginView
class CustomLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        page = BaseLayout(
            LoginPageComponent(request, form),
            title="Login",
            request=request
        )
        return HttpResponse(page)

    def post(self, request, *args, **kwargs):
        self.form = self.get_form()
        if self.form.is_valid():
            # form_valid() handles the login and returns the redirect response
            return self.form_valid(self.form)
        else:
            # form_invalid() re-renders the form with errors
            return self.form_invalid(self.form)

    def form_invalid(self, form):
        # Re-render the page with the form containing errors
        page = BaseLayout(
            [LoginPageComponent(self.request, form),],
            title="Login",
            request=self.request
        )
        return HttpResponse(page)


# A custom view that subclasses Allauth's SignupView
class CustomSignupView(SignupView):
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        page = BaseLayout(
            SignupPageComponent(request, form),
            title="Sign Up",
            request=request
        )
        return HttpResponse(page, content_type="text/html")

    def post(self, request, *args, **kwargs):
        self.form = self.get_form()
        if self.form.is_valid():
            return self.form_valid(self.form)
        else:
            return self.form_invalid(self.form)

    def form_invalid(self, form):
        page = BaseLayout(
            SignupPageComponent(self.request, form),
            title="Sign Up",
            request=self.request
        )
        return HttpResponse(page)
