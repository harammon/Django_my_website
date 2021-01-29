from django.shortcuts import render
from .models import Post
from django.views.generic import ListView

# Create your views here.

class PostList(ListView):   # 장고가 재공해주는 선물! 리스트를 출력할 때 유용하게 사용 가능하다. -> def index(request)사용 대체!
    model = Post

    def get_queryset(self):
        return Post.objects.order_by('-created')    # 작성일의 역순으로 출력

#def index(request):
#    posts = Post.objects.all()  # 객체 전부를 전달 -> 현재 객체의 __str__()의 형식을 변경했으니, 출력하면 변경된 형식대로 출력할 것임
#    return render(request, 'blog/index.html', {'posts':posts, 'a_plus_b': 1+3})     # index.html에 전달하고 싶은 내용을 변수에 담아 전달!