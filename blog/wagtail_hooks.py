# from django.contrib.admin import ModelAdmin
from wagtail import hooks
from wagtail.admin.views.generic import CreateView
from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup

from .models import BlogCategory, BlogPage


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


class BlogPageCreateView(CreateView):
    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.moderation_status = 'pending'
        return super().form_valid(form)


class BlogPageAdmin(ModelViewSet):
    model = BlogPage
    create_view_class = BlogPageCreateView
    menu_label = 'Blog Posts'
    exclude_form_fields = ('id',)
    menu_icon = 'doc-full'
    list_display = ('title', 'moderation_status', 'date')
    list_filter = ('moderation_status', 'owner')
    search_fields = ('title', 'intro', 'body')

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     return qs.filter(author=request.user)

class BlogGroup(ModelViewSetGroup):
    menu_label = 'Blog Management'
    icon = 'folder-open-inverse'
    menu_order = 200
    items = (BlogCategoryAdmin, BlogPageAdmin, )



@hooks.register("register_admin_viewset")
def register_viewset():
    return BlogGroup()
