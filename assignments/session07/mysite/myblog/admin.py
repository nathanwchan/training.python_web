from django.contrib import admin
from myblog.models import Post
from myblog.models import Category

class CategoryInline(admin.TabularInline):
    model = Category.posts.through

class PostAdmin(admin.ModelAdmin):
    inlines = [CategoryInline,]

class CategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'description')

admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
