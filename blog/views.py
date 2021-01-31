from django.shortcuts import render
from .models import Post, Category
from django.views.generic import ListView, DetailView

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


class PostDetail(DetailView):
    model = Post        # 모델이름_detail 이라는 html 템플릿 필요함!!!!  ->해당 html에서 object.으로 접근 가능

# def post_detail(request, pk):
#     blog_post = Post.objects.get(pk=pk)     #read more 눌렀을 때 해당 블로그 포스트 '한 개'만 불러옴
#     return render(request, 'blog/post_detail.html', {'blog_post' : blog_post })    #request를 넘겨주는 것은 규칙, 그리고 템플릿 이름 / 넘겨줄 것(딕셔너리)
