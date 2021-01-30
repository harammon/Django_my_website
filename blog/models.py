from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()
    head_image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True)   # 이미지가 프로젝트 내에 추가 되게 하지 않기 위해 setting 설정
                                                    # 이렇게 하면 업로드 날짜에 맞는 폴더에 저장됨!
    created = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1)   #작성자 user와(미리 정의) 연결!, 참조 무결성 제약


    def __str__(self):
        return '{} :: {}'.format(self.title, self.author)
