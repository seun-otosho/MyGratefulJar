from wagtail.admin.views.generic import IndexView, CreateView
from wagtail.log_actions import log


class CustomCreateView(CreateView, ):
    def save_instance(self):
        instance = self.form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        log(instance=instance, action="wagtail.create", content_changed=True)
        return instance


class CustomIndexView(IndexView, ):
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        queryset = self.search_queryset(queryset)
        return queryset
