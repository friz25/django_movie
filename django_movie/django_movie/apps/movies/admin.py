from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from modeltranslation.admin import TranslationAdmin

from .models import Category, Actor, RatingStar, Rating, Reviews, Movie, MovieShots, Genre, Director

admin.site.sit_title = "Djano Movies"
admin.site.site_header = "Djano Movies"

admin.site.register(RatingStar)

from ckeditor_uploader.widgets import CKEditorUploadingWidget

class MovieAdminForm(forms.ModelForm):
    """Текстовый редактор CKEditor"""
    description_ru = forms.CharField(label="Описание", widget=CKEditorUploadingWidget())
    description_en = forms.CharField(label="Description", widget=CKEditorUploadingWidget())

    class Meta:
        model = Movie
        fields = '__all__'

@admin.register(Actor)
class ActorAdmin(TranslationAdmin):
    """Актёры и режжисеры"""
    list_display = ("name", "age", "get_image")
    readonly_fields = ("get_image", )

    def get_image(self, obj):
        try:
            return mark_safe(f'<img src={obj.image.url} width="100" height="120">')
        except:
            return ""


    get_image.short_descriprion = "Изображение"

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Рейтинги"""
    list_display = ("star", "movie", "ip")


@admin.register(MovieShots)
class MovieShotsAdmin(TranslationAdmin):
    """Кадры из фильма"""
    list_display = ("title", "movie", "get_image")
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        try:
            return mark_safe(f'<img src={obj.image.url} width="150" height="100">')
        except:
            return ""

    get_image.short_description = "Изображение"

@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    """Категории"""
    # fields = ['name', 'rating']
    # exclude = ['slug']
    # readonly_fields = ['year']
    prepopulated_fields = {'url': ('name',)}
    # filter_horizontal = ['directors', 'actors', 'genres']
    # filter_vertical = ['actors']
    list_display = ['id', 'name', 'description']
    list_display_links = ['name']
    list_editable = ['description']
    # ordering = ['rating', 'name']
    list_per_page = 10
    # actions = ['set_dollars', 'set_euro']
    search_fields = ['name', 'description']  # + строка поиска
    # list_filter = ['title', 'year', 'country', 'budget', 'draft']  # +фильтры справа


class ReviewInline(admin.TabularInline):
    """Отзывы (на странице фильма)"""
    model = Reviews
    extra = 1
    readonly_fields = ['parent', 'name', 'email']

@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    """Отзывы"""
    # fields = ['name', 'rating']
    # exclude = ['parent']
    readonly_fields = ['parent', 'name', 'email']
    # prepopulated_fields = {'url': ('title',)}
    # filter_horizontal = ['movie']
    # filter_vertical = ['actors']
    list_display = ['name', 'email', 'text', 'parent', 'movie', 'id']
    list_editable = ['email', 'text', 'movie']
    # ordering = ['rating', 'name']
    list_per_page = 10
    # actions = ['set_dollars', 'set_euro']
    search_fields = ['name', 'text']  # + строка поиска
    # list_filter = ['title', 'year', 'country', 'budget', 'draft']  # +фильтры справа

class MovieShotsInline(admin.TabularInline):
    """Кадры из фильма (на странице фильма)"""
    model = MovieShots
    extra = 1
    readonly_fields = ['get_image']

    def get_image(self, obj):
        try:
            return mark_safe(f'<img src={obj.image.url} width="150" height="100">')
        except:
            return ""


    get_image.short_description = "Изображение"

@admin.register(Movie)
class MovieAdmin(TranslationAdmin):
    """Фильмы"""
    # fields = ['name', 'rating']
    # exclude = ['slug']
    form = MovieAdminForm #CKEditor
    readonly_fields = ['get_poster_image']
    # prepopulated_fields = {'url': ('title', )}
    filter_horizontal = ['directors', 'actors', 'genres']
    # filter_vertical = ['actors']
    list_display = ['title', 'year', 'country', 'world_premier', 'budget', 'fees_in_usa', 'fees_in_world', 'draft']
    list_filter = ['category', 'year']
    list_editable = ['year', 'country', 'budget', 'fees_in_usa', 'fees_in_world',]
    # ordering = ['rating', 'name']
    list_per_page = 10
    actions = ['unpublish', 'publish']
    search_fields = ['title', 'year', 'category__name']  # + строка поиска
    # list_filter = ['title', 'year', 'country', 'budget', 'draft']  # +фильтры справа
    inlines = [MovieShotsInline, ReviewInline] #список [комментов, кадров из фильма] к фильму
    save_on_top = True
    save_as = True
    # fields = (("budget", "fees_in_usa", "fees_in_world"),)
    fieldsets = (
        (None, {
            "fields": (('title', 'tagline'),)
        }),
        (None, {
            "fields": (('description', 'poster', 'get_poster_image'),)
        }),
        (None, {
            "fields": (('year', 'world_premier', 'country'),)
        }),
        (None, {
            "fields": (('actors'),)
        }),
        (None, {
            "fields": (('directors'),)
        }),
        (None, {
            "fields": (('genres'),)
        }),
        (None, {
            "fields": (('category'),)
        }),
        ("Бюджеты и Сборы", {
            "classes": ("collapse",),
            "fields": (('budget', 'fees_in_usa', 'fees_in_world'),)
        }),
        (None, {
            "fields": (('url', 'draft'),)
        }),
    )

    def get_poster_image(self, obj):
        return mark_safe(f'<img src={obj.poster.url} width="100" height="120">')

    get_poster_image.short_description = "Постер"

    def unpublish(self, request, queryset):
        """Снять с публикации"""
        row_update = queryset.update(draft=True)
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записей были обновлены"
        self.message_user(request, f'{message_bit}')

    def publish(self, request, queryset):
        """Опубликовать"""
        row_update = queryset.update(draft=False)
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записей были обновлены"
        self.message_user(request, f'{message_bit}')

    publish.short_description = "Опубликовать"
    publish.allowed_permissions = ('change', )#у user'a должны быть права на "изменение"

    unpublish.short_description = "Снять с публикации"
    unpublish.allowed_permissions = ('change', )#у user'a должны быть права на "изменение"



@admin.register(Genre)
class GenreAdmin(TranslationAdmin):
    """Жанры"""
    # fields = ['name', 'rating']
    # exclude = ['slug']
    # readonly_fields = ['year']
    prepopulated_fields = {'url': ('name',)}
    # filter_horizontal = ['directors', 'actors', 'genres']
    # filter_vertical = ['actors']
    list_display = ['name', 'description']
    list_editable = ['description']
    # ordering = ['rating', 'name']
    list_per_page = 10
    # actions = ['set_dollars', 'set_euro']
    search_fields = ['name', 'description']  # + строка поиска
    # list_filter = ['title', 'year', 'country', 'budget', 'draft']  # +фильтры справа


