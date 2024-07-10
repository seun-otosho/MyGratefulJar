from wagtail.admin.ui.tables import UpdatedAtColumn
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from config.wagtail_hooks import CustomCreateView
from .models import Category, Income


class CategoryViewSet(SnippetViewSet):
    model = Category
    icon = "crosshairs"
    menu_label = "Categories"
    add_to_admin_menu = True
    menu_name = "categories"
    menu_order = 300

    add_view_class = CustomCreateView


# Instead of using @register_snippet as a decorator on the model class,
# register the snippet using register_snippet as a function and pass in
# the custom SnippetViewSet subclass.
register_snippet(CategoryViewSet)


class IncomeViewSet(SnippetViewSet):
    model = Income
    add_to_admin_menu = True
    icon = "crosshairs"
    list_display = ["category", "amount", "date", UpdatedAtColumn()]
    list_filter = {"category": ["exact"], "amount": ["icontains"]}
    list_per_page = 10
    menu_label = "Incomes"
    menu_name = "incomes"
    menu_order = 400

    add_view_class = CustomCreateView


register_snippet(IncomeViewSet)
