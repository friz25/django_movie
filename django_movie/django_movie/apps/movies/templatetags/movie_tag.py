from django import template
from ..models import Category, Movie, Genre

register = template.Library()

@register.simple_tag()
def get_categories():
    """Вывод всех категорий"""
    return Category.objects.all()

@register.simple_tag()
def get_genres():
    """Вывод всех Жанров"""
    return Genre.objects.all()

@register.inclusion_tag('movies/tags/last_movie.html')
def get_last_movies(count):
    movies = Movie.objects.order_by("id")[:count]
    return {"last_movies": movies}

# def get_context_data(self, *args, **kwargs):
#     context = super().get_context_data(*args, **kwargs)
#     context["categories"] = Category.objects.all()
#     return context