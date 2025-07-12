# accounts/views.py
from allauth.account.views import (
    LoginView, SignupView, PasswordResetView, PasswordResetDoneView, PasswordResetFromKeyView,
    PasswordResetFromKeyDoneView, PasswordChangeView
)
from django.http import HttpResponse

from themes.nemesis.main import BaseLayout
from .components import (
    LoginPageComponent, SignupPageComponent, PasswordResetRequestComponent, PasswordResetDoneComponent,
    PasswordResetFromKeyComponent, PasswordResetFromKeyDoneComponent, PasswordChangeComponent
)


# A custom view that subclasses Allauth's LoginView
class CustomLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        page = BaseLayout(
            request,
            "Login",
            "",
            LoginPageComponent(request, form),
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
            self.request,
            "Login",
            "",
            LoginPageComponent(self.request, form),
        )
        return HttpResponse(page)


# A custom view that subclasses Allauth's SignupView
class CustomSignupView(SignupView):
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        page = BaseLayout(
            request,
            "Sign Up",
            "",
            SignupPageComponent(request, form),
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
            self.request,
            "Sign Up",
            SignupPageComponent(self.request, form),
        )
        return HttpResponse(page)


# --- NEW VIEWS FOR PASSWORD RESET ---

class CustomPasswordResetView(PasswordResetView):
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        page = BaseLayout(
            request, "Reset Password", "", PasswordResetRequestComponent(request, form))
        return HttpResponse(page)

    def form_invalid(self, form):
        page = BaseLayout(
            self.request, "Reset Password", "", PasswordResetRequestComponent(self.request, form), )
        return HttpResponse(page)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    def get(self, request, *args, **kwargs):
        page = BaseLayout(
            request, "Reset Email Sent", "", PasswordResetDoneComponent(), )
        return HttpResponse(page)


class CustomPasswordResetFromKeyView(PasswordResetFromKeyView):
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        page = BaseLayout(
            request, "Set New Password", "", PasswordResetFromKeyComponent(request, form), )
        return HttpResponse(page)

    def form_invalid(self, form):
        page = BaseLayout(
            self.request, "Set New Password", "", PasswordResetFromKeyComponent(self.request, form), )
        return HttpResponse(page)


class CustomPasswordResetFromKeyDoneView(PasswordResetFromKeyDoneView):
    def get(self, request, *args, **kwargs):
        page = BaseLayout(
            request, "Password Reset", "", PasswordResetFromKeyDoneComponent(), )
        return HttpResponse(page)


# --- NEW VIEW FOR PASSWORD CHANGE ---

class CustomPasswordChangeView(PasswordChangeView):
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        page = BaseLayout(
            request, "Change Password", "", PasswordChangeComponent(request, form), )
        return HttpResponse(page)

    def form_invalid(self, form):
        page = BaseLayout(
            self.request, "Change Password", "", PasswordChangeComponent(self.request, form), )
        return HttpResponse(page)
