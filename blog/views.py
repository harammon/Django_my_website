from django.shortcuts import render
from .models import Post
# Create your views here.


def index(request):
    posts = Post.objects.all()  # 객체 전부를 전달 -> 현재 객체의 __str__()의 형식을 변경했으니, 출력하면 변경된 형식대로 출력할 것임
    return render(request, 'blog/index.html', {'posts':posts, 'a_plus_b': 1+3})     # index.html에 전달하고 싶은 내용을 변수에 담아 전달!