from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import CommentForm


from django.contrib import messages
from .models import BlogPage
from .forms import CommentForm

def add_comment(request, page_id):
    blog_page = get_object_or_404(BlogPage, id=page_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.page = blog_page
            comment.save()
            messages.success(request, 'Your comment has been added successfully!')
        else:
            messages.error(request, 'There was an error with your comment. Please try again.')
    return redirect(blog_page.url)


# def home(request):
#     posts = Post.objects.all().order_by('-created_date')
#     return render(request, 'home.html', {'posts': posts})

# def signup(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')
#     else:
#         form = UserCreationForm()
#     return render(request, 'signup.html', {'form': form})

# @login_required
# def create_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author = request.user
#             post.save()
#             form.save_m2m()  # Save tags
#             return redirect('home')
#     else:
#         form = PostForm()
#     return render(request, 'create_post.html', {'form': form})

# def post_detail(request, pk):
#     post = Post.objects.get(pk=pk)    
#     comments = post.comments.filter(parent=None)
#     new_comment = None

#     if request.method == 'POST':
#         comment_form = CommentForm(data=request.POST)
#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.post = post
#             new_comment.author = request.user
#             new_comment.save()
#             return redirect('post_detail', pk=post.pk)
#     else:
#         comment_form = CommentForm()

#     return render(request, 'post_detail.html', {
#         'post': post,
#         'comments': comments,
#         'new_comment': new_comment,
#         'comment_form': comment_form
#     })

# @login_required
# def add_comment_to_comment(request, post_pk, comment_pk):
#     parent_comment = get_object_or_404(Comment, pk=comment_pk)
#     if request.method == 'POST':
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             new_comment = form.save(commit=False)
#             new_comment.post = parent_comment.post
#             new_comment.author = request.user
#             new_comment.parent = parent_comment
#             new_comment.save()
#             return redirect('post_detail', pk=post_pk)
#     else:
#         form = CommentForm()
#     return render(request, 'add_comment_to_comment.html', {'form': form})

