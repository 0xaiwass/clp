from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import *
from django.views.generic import DetailView
from .forms import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
########################################################################
class BlogsView(View):
    def get(self, request):
        posts_qs = BlogPost.objects.filter(published=True).order_by('-created_at')
        paginator = Paginator(posts_qs, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'posts': page_obj,
            'page_obj': page_obj
        }
        return render(request, 'blogs/blogs.html', context)
########################################################################
class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blogs/detail.html'
    context_object_name = 'blog'  # keep consistent with your template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(active=True)
        context['form'] = CommentForm()
        return context
########################################################################
class TagView(View):
    def get(self, request, slug):
        tag = get_object_or_404(Tag, slug=slug)
        posts = tag.posts.filter(published=True).order_by('-created_at')
        return render(request, 'blogs/tag.html', {'tag': tag, 'posts': posts})
########################################################################

@method_decorator(login_required, name='dispatch')
class AddCommentView(View):
    def post(self, request, slug):
        blog = get_object_or_404(BlogPost, slug=slug)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.blog = blog
            comment.active = False  # admin moderation
            comment.save()
            return redirect('blogs:detail', slug=slug)

        return render(request, 'blogs/detail.html', {
            'post': blog,
            'comments': blog.comments.filter(active=True),
            'form': form,
        })