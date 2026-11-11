from django.contrib import admin

from .models import Category, Comment, Location, Post


class PublishedAdmin(admin.ModelAdmin):
    list_filter = ('is_published',)
    readonly_fields = ('created_at',)


@admin.register(Category)
class CategoryAdmin(PublishedAdmin):
    list_display = (
        'id',
        'title',
        'slug',
        'is_published',
        'created_at',
    )
    search_fields = ('title', 'description', 'slug')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(PublishedAdmin):
    list_display = (
        'id',
        'name',
        'is_published',
        'created_at',
    )
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(PublishedAdmin):
    list_display = (
        'id',
        'title',
        'author',
        'category',
        'location',
        'pub_date',
        'is_published',
    )
    list_filter = (
        'is_published',
        'category',
        'location',
        'pub_date',
    )
    search_fields = ('title', 'text', 'author__username')
    list_select_related = ('author', 'category', 'location')
    date_hierarchy = 'pub_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'post',
        'author',
        'text',
        'created_at',
    )
    search_fields = (
        'text',
        'author__username',
        'post__title',
    )
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    list_select_related = ('post', 'author')
