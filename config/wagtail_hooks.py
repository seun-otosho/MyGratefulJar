from wagtail.log_actions import log
from wagtail.snippets.views.snippets import CreateView


class CustomCreateView(CreateView, ):

    def save_instance(self):
        instance = self.form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        log(instance=instance, action="wagtail.create", content_changed=True)
        return instance
