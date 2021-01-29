from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    created = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1)   #작성자 user와(미리 정의) 연결!, 참조 무결성 제약


    def __str__(self):
        return '{} :: {}'.format(self.title, self.author)


