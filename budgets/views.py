from wagtail.admin.ui.tables import UpdatedAtColumn
from wagtail.admin.viewsets.model import ModelViewSet

from budgets.models import Category, Income, BudgetItem, Expense
from config.wagtail_hooks import CustomCreateView, CustomIndexView


# Create your views here.
class CategoryViewSet(ModelViewSet):
    model = Category
    icon = "crosshairs"
    menu_label = "Categories"
    add_to_admin_menu = True
    menu_name = "categories"
    menu_order = 300
    form_fields = ["name", ]


categories_viewset = CategoryViewSet("categories")


class IncomeViewSet(ModelViewSet):
    model = Income
    add_to_admin_menu = True
    icon = "crosshairs"
    list_display = ["category", "amount", "date", UpdatedAtColumn()]
    list_filter = {"category": ["exact"], "amount": ["icontains"]}
    list_per_page = 10
    menu_label = "Incomes"
    menu_name = "incomes"
    menu_order = 400
    form_fields = ["date", "amount", "category", "description", ]

    add_view_class = CustomCreateView
    index_view_class = CustomIndexView


incomes_viewset = IncomeViewSet("incomes")


class BudgetItemViewSet(ModelViewSet):
    model = BudgetItem
    add_to_admin_menu = True
    icon = "crosshairs"
    list_display = ["category", "amount", "date", UpdatedAtColumn()]
    list_filter = {"category": ["exact"], "amount": ["icontains"]}
    list_per_page = 10
    menu_label = "Budget Items"
    menu_name = "budgets"
    menu_order = 400
    form_fields = ["date", "amount", "category", ]

    add_view_class = CustomCreateView


budgets_viewset = BudgetItemViewSet("budgets")


class ExpenseViewSet(ModelViewSet):
    model = Expense
    add_to_admin_menu = True
    icon = "crosshairs"
    list_display = ["category", "amount", "date", UpdatedAtColumn()]
    list_filter = {"category": ["exact"], "amount": ["icontains"]}
    list_per_page = 10
    menu_label = "Expenses"
    menu_name = "expenses"
    menu_order = 500
    form_fields = ["date", "amount", "category", "description", ]

    add_view_class = CustomCreateView


expense_viewset = ExpenseViewSet("expenses")
