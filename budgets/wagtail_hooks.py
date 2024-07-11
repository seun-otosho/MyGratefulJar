from wagtail import hooks

from .views import categories_viewset, incomes_viewset, budgets_viewset, expense_viewset


@hooks.register("register_admin_viewset")
def register_viewset():
    return categories_viewset


@hooks.register("register_admin_viewset")
def register_viewset():
    return incomes_viewset


@hooks.register("register_admin_viewset")
def register_viewset():
    return budgets_viewset


@hooks.register("register_admin_viewset")
def register_viewset():
    return expense_viewset
