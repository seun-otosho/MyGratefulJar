from wagtail import hooks

from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup

from .models import Category


from .models import BlogCategory

class BlogCategoryAdmin(ModelViewSet):
    model = BlogCategory
    menu_label = 'Blog Categories'
    icon = 'tag'
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ('name',)
    search_fields = ('name',)

# class UserProfileAdmin(ModelAdmin):
#     model = UserProfile
#     menu_label = 'User Profiles'
#     menu_icon = 'user'
#     menu_order = 300
#     add_to_settings_menu = False
#     exclude_from_explorer = False
#     list_display = ('user', 'following_count')
#     search_fields = ('user__username',)

#     def following_count(self, obj):
#         return obj.following.count()
#     following_count.short_description = 'Following'


category_viewset = BlogCategoryAdmin("category") 

class BlogGroup(ModelViewSetGroup):
    menu_label = 'Blog Management'
    icon = 'folder-open-inverse'
    menu_order = 200
    items = (BlogCategoryAdmin, )


class CategoryViewSet(ModelViewSet):
    add_to_admin_menu = True
    model = Category
    form_fields = ["name", ]
    menu_label = "Category"
    menu_name = "category"
    icon = "pilcrow"



@hooks.register("register_admin_viewset")
def register_viewset():
    return BlogGroup()
