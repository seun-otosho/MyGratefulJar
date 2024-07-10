# myapp/wagtail_hooks.py
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Category, Income


class CategoryViewSet(SnippetViewSet):
    model = Category
    icon = "crosshairs"
    menu_label = "Categories"
    # menu_name = "categories"
    menu_order = 300

    panels = [
        FieldPanel("name"),
        # FieldPanel("text"),
    ]


# Instead of using @register_snippet as a decorator on the model class,
# register the snippet using register_snippet as a function and pass in
# the custom SnippetViewSet subclass.
register_snippet(CategoryViewSet)


class IncomeViewSet(SnippetViewSet):
    model = Income
    icon = "crosshairs"
    menu_label = "Incomes"
    # menu_name = "incomes"
    menu_order = 400

    panels = [
        FieldPanel("name"),
        # FieldPanel("text"),
    ]


register_snippet(IncomeViewSet)
