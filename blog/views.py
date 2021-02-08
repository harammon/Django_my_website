from django.shortcuts import render, redirect
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin   #로그인 한 사람만 접속 가능하게 하도록
# 장고에서 제공하는 선물!! 리스트를 쉽게 생성할 수 있다!
class PostList(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.order_by('-created')

    # 이 함수는 장고에서 기본으로 정해놓은것... 이해하려 하지 말고 가져다가 쓰기!!
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()           # get은 하나만, all은 전부, filter는 특정 조건에 해당하는 것만 가져옴
        return context
    # def index(request):
    #     posts = Post.objects.all()    # db 명령
    #
    #     return render(
    #         request,
    #         'blog/index.html',
    #         {
    #             'posts': posts,
    #         }
    #     )

class PostListByTag(ListView):
    def get_queryset(self):
        tag_slug = self.kwargs['slug']
        tag = Tag.objects.get(slug=tag_slug)

        return tag.post_set.order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()           # get은 하나만, all은 전부, filter는 특정 조건에 해당하는 것만 가져옴
        tag_slug = self.kwargs['slug']
        context['tag'] = Tag.objects.get(slug=tag_slug)

        return context



class PostDetail(DetailView):
    model = Post        # 모델이름_detail 이라는 html 템플릿 필요함!!!!  ->해당 html에서 object.으로 접근 가능

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()           # get은 하나만, all은 전부, filter는 특정 조건에 해당하는 것만 가져옴
        context['comment_form'] = CommentForm()

        return context

# def post_detail(request, pk):
#     blog_post = Post.objects.get(pk=pk)     #read more 눌렀을 때 해당 블로그 포스트 '한 개'만 불러옴
#     return render(request, 'blog/post_detail.html', {'blog_post' : blog_post })    #request를 넘겨주는 것은 규칙, 그리고 템플릿 이름 / 넘겨줄 것(딕셔너리)

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = [
        'title', 'content', 'head_image', 'category', 'tags'
    ]
# 형식이 맞는지 확인하는 함수(오버라이딩)
    def form_valid(self, form):
        current_user = self.request.user
        # 로그인 한 사용자만 포스트 생성을 할 수 있도록
        if current_user.is_authenticated:
            form.instance.author = current_user
            return super(type(self), self).form_valid(form)
        else:
            return redirect('/blog/')

class PostUpdate(UpdateView):
    model = Post
 #   fields = '__all__'  # 포스트 모델에 있는 모든 필드를 가져오라는 의미
    fields = [
        'title', 'content', 'head_image', 'category', 'tags'
    ]

# 이부분 어려움!! 복습 필요!!
class PostListByCategory(ListView):

    def get_queryset(self):
        slug = self.kwargs['slug']      # 이런 식으로 url에서 slug를 가져올 수 있다.

        if slug == '_none':
            category = None
        else:
            category = Category.objects.get(slug=slug)
        return Post.objects.filter(category=category).order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()           # get은 하나만, all은 전부, filter는 특정 조건에 해당하는 것만 가져옴

        slug = self.kwargs['slug']  # 이런 식으로 url에서 slug를 가져올 수 있다.
        if slug == '_none':
            context['category'] = '미분류'
        else:
            category = Category.objects.get(slug=slug)
            context['category'] = category
            # context['title'] = 'Blog - {}'.format(category.name)
        return context

def new_comment(request, pk):
    post = Post.objects.get(pk=pk)

    if request.method=='POST':
        comment_form555555 = CommentForm(request.POST)
        if comment_form555555.is_valid(): # 유효한 경우 필요한 것을 채워줘야함. 현재 form에는 text만 받아온 상태.. model 에 저장되어 있는 author 등을 받아와야함
            comment = comment_form555555.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect(comment.get_absolute_url()) # 해당 댓글로 바로 이동하기 위해 get absolute url 함수 만들었음 -> models에 있음
    else:
        return redirect('/blog/')

class CommentUpdate(UpdateView):
    model = Comment
    form_class = CommentForm

    def get_object(self, queryset = None):
        comment = super(CommentUpdate, self).get_object()  #super는 deleteview를 지칭
        if comment.author != self.request.user:
            raise PermissionError('Comment를 수정할 권한이 없습니다.')
        return comment


def delete_comment(request, pk):
    comment = Comment.objects.get(pk=pk)

    if request.user == comment.author:
        post = comment.post
        comment.delete()
        return redirect(post.get_absolute_url() + '#comment-list')
    else:
        raise PermissionError('Comment를 삭제할 권한이 없습니다.')

# class CommentDelete(DeleteView):
#     model = Comment
#
#     def get_object(self, queryset = None):
#         comment = super(CommentDelete, self).get_object()  #super는 deleteview를 지칭
#         if comment.author != self.request.user:
#             raise PermissionError('Comment 삭제 권한이 없습니다.')
#         return comment
#
#     def get_success_url(self):
#         post = self.get_object().post   #get_object()는 클래스에서 제공하는 함수!
#         return post.get_absolute_url() + '#comment-list'    #id 주소를 추가


