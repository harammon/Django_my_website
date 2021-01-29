from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):   # settings의 app에 등록해줘야 함
    title = models.CharField(max_length=30)     # charfield는 길이 필수
    content = models.TextField()    # 길이 제한 x

    created = models.DateTimeField()    # 글 작성 날짜, 시간
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1)   #작성자 user와(미리 정의) 연결!, 참조 무결성 제약
