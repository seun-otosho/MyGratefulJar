from django.shortcuts import render


def not_found(request, exception=None):
    render(request, 'nemesis/error.html')
