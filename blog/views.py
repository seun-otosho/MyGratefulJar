from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CommentForm, BlogPostForm
from .models import BlogPage, BlogIndexPage


def blog_index(request):
    blog_index = BlogIndexPage.objects.first()
    if blog_index:
        return blog_index.serve(request)
    return render(request, 'blog/blog_index_page.html')


@login_required
def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            blog_index = BlogIndexPage.objects.first()
            blog_page = BlogPage(
                title=form.cleaned_data['title'],
                intro=form.cleaned_data['intro'],
                body=form.cleaned_data['body'],
                owner=request.user
            )
            blog_index.add_child(instance=blog_page)
            blog_page.save_revision().publish()
            messages.success(request, 'Your blog post has been created!')
            return redirect(blog_page.url)
    else:
        form = BlogPostForm()
    return render(request, 'blog/create_blog_post.html', {'form': form})


def blog_post(request, slug):
    blog_page = get_object_or_404(BlogPage, slug=slug)
    comments = blog_page.comments.all()
    new_comment = None

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to comment.")
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.page = blog_page
            new_comment.author = request.user.username
            new_comment.email = request.user.email
            new_comment.save()
            messages.success(request, 'Your comment has been added successfully!')
            return redirect('blog_post', slug=slug)
    else:
        comment_form = CommentForm()

    return render(request, 'blog/blog_page.html', {
        'page': blog_page,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'user': request.user
    })


@login_required
def add_comment(request, page_id):
    blog_page = get_object_or_404(BlogPage, id=page_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.page = blog_page
            comment.author = request.user.username
            comment.email = request.user.email
            comment.save()
            messages.success(request, 'Your comment has been added successfully!')
        else:
            messages.error(request, 'There was an error with your comment. Please try again.')
    return redirect(blog_page.url)
