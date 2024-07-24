from wagtail import hooks

from wagtail.admin.viewsets.model import ModelViewSet

from .models import Category

class CategoryViewSet(ModelViewSet):
    add_to_admin_menu = True
    model = Category
    form_fields = ["name", ]
    menu_label = "Category"
    menu_name = "category"
    icon = "pilcrow"


category_viewset = CategoryViewSet("category") 



@hooks.register("register_admin_viewset")
def register_viewset():
    return category_viewset
