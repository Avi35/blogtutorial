from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView,DeleteView
from .models import Article
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import UpdateView
from tinymce.widgets import TinyMCE
from .models import Article
from django import forms


class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = Article
        fields = ['title', 'content', 'featured']




class Index(ListView):
   model = Article
   queryset = Article.objects.all().order_by('-date')
   template_name = 'blog/index.html'
   paginate_by = 1


class Featured(ListView):
	model = Article
	queryset = Article.objects.filter(featured=True).order_by('-date')
	template_name = 'blog/featured.html'
	paginate_by = 1



class DetailArticleView(DetailView):
	model = Article
	template_name = 'blog/blog_post.html'

	def get_context_data(self, *args, **kwargs):
		context = super(DetailArticleView, self).get_context_data(*args, **kwargs)
		context['liked_by_user'] = False
		article = Article.objects.get(id=self.kwargs.get('pk'))
		if article.likes.filter(pk=self.request.user.id).exists():
			context['liked_by_user'] = True
		return context


	def get_context_data(self, *args, **kwargs):
		context = super(DetailArticleView, self).get_context_data(*args, **kwargs)
		context['tinymce_enabled'] = True
		return context




class LikeArticle(View):
	def post(self, request, pk):
		article = Article.objects.get(id=pk)
		if article.likes.filter(pk=self.request.user.id).exists():
			article.likes.remove(request.user.id)
		else:
			article.likes.add(request.user.id)

		article.save()
		return redirect('detail_article', pk)


class DeleteArticleView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Article
	template_name = 'blog/blog_delete.html'
	success_url = reverse_lazy ('index')

	def test_func(self):
		article = Article.objects.get(id=self.kwargs.get('pk'))
		return self.request.user.id == article.author.id


class EditArticleView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/blog_edit.html'
    success_url = reverse_lazy('index')


    def test_func(self):
        article = self.get_object()
        if self.request.user == article.author:
            return True
        return False
