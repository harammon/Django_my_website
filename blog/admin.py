from django.contrib import admin
from .models import Post, Category, Tag


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}       # 미리 만들어지는 필드       -> slug 이름이 name으로 자동으로 생성되도록!!!

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}       # 미리 만들어지는 필드       -> slug 이름이 name으로 자동으로 생성되도록!!!


admin.site.register(Post)
admin.site.register(Category, CategoryAdmin)        # 슬러그를 위해 추가해줘야함
admin.site.register(Tag, TagAdmin)        # 슬러그를 위해 추가해줘야함
