from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown

class Category(models.Model):
    name = models.CharField(max_length=25, unique=True)  # 이름이 중복되는 것을 방지
    description = models.TextField(blank = True)

    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/blog/category/{}/'.format(self.slug)        # 슬러그를 자동으로 생성하는 것이 목표

    class Meta:     # 관리자 페이지에서 이름 그대로 가져와서 Category's'가 되었는데, 어색하기 때문에 수정해주기 위함
        verbose_name_plural = 'categories'


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/blog/tag/{}/'.format(self.slug)        # 슬러그를 자동으로 생성하는 것이 목표



class Post(models.Model):
    title = models.CharField(max_length=30)
    # content = models.TextField()
    content = MarkdownxField()
    head_image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True)   # 이미지가 프로젝트 내에 추가 되게 하지 않기 위해 setting 설정
                                                    # 이렇게 하면 업로드 날짜에 맞는 폴더에 저장됨!
    created = models.DateTimeField(auto_now_add=True) # 포스트가 생성이 될 때 created에 자동으로 담아주게 된다.
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1)   #작성자 user와(미리 정의) 연결!, 참조 무결성 제약
    category = models.ForeignKey(Category, blank = True, null = True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank = True)

# 페이지네이션 때문에 추가해줌
    class Meta:
        ordering = ['-created', ]

    def __str__(self):
        return '{} :: {}'.format(self.title, self.author)

    # 관리자 화면에서 view on site 구축 함수!! 장고 내장..!!
    def get_absolute_url(self):
        return '/blog/{}/'.format(self.pk)

    def get_update_url(self):
        return self.get_absolute_url() + 'update/'

    def get_markdown_content(self):
        return markdown(self.content)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = MarkdownxField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)    # 새로 생성됐을 때 저절로 시간이 들어가게끔
    modified_at = models.DateTimeField(auto_now=True)

    def get_markdown_content(self):
        return markdown(self.text)

    def get_absolute_url(self):
        return self.post.get_absolute_url() + '#comment-id-{}'.format(self.pk)  # 해당 댓글로 바로 이동하기 위함.