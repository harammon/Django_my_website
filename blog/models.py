from django.db import models
from django.contrib.auth.models import User


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

class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()
    head_image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True)   # 이미지가 프로젝트 내에 추가 되게 하지 않기 위해 setting 설정
                                                    # 이렇게 하면 업로드 날짜에 맞는 폴더에 저장됨!
    created = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1)   #작성자 user와(미리 정의) 연결!, 참조 무결성 제약

    category = models.ForeignKey(Category, blank = True, null = True, on_delete=models.SET_NULL)
    def __str__(self):
        return '{} :: {}'.format(self.title, self.author)

    # 관리자 화면에서 view on site 구축 함수!! 장고 내장..!!
    def get_absolute_url(self):
        return '/blog/{}/'.format(self.pk)



