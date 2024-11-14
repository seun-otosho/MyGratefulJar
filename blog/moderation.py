# blog/moderation.py
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

from blog.models import BlogPage

User = get_user_model()

class ContentModerator:
    @staticmethod
    def moderate_content(content, moderator=None, status='approved', notes=''):
        """
        Moderate any content (BlogPage or Comment)
        """
        content.moderation_status = status
        if moderator:
            content.moderated_by = moderator
        content.moderation_notes = notes
        content.save()

        # Notify content author
        if hasattr(content, 'author'):
            context = {
                'content': content,
                'status': status,
                'notes': notes,
            }
            send_mail(
                f'Your content has been {status}',
                render_to_string('blog/emails/moderation_notification.txt', context),
                'from@yourdomain.com',
                [content.author.email],
                html_message=render_to_string('blog/emails/moderation_notification.html', context),
            )

@receiver(post_save, sender=BlogPage)
def handle_post_moderation(sender, instance, created, **kwargs):
    """
    Handle automatic moderation tasks when a post is saved
    """
    if created and instance.moderation_status == 'draft':
        # Notify moderators about new content
        moderators = User.objects.filter(is_staff=True)
        context = {
            'post': instance,
            'moderation_url': reverse('admin:blog_blogpage_change', args=[instance.id]),
        }
        for moderator in moderators:
            send_mail(
                'New content requires moderation',
                render_to_string('blog/emails/new_content_notification.txt', context),
                'from@yourdomain.com',
                [moderator.email],
                html_message=render_to_string('blog/emails/new_content_notification.html', context),
            )
