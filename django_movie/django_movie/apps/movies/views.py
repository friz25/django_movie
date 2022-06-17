from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import ListView, View, DetailView

from .models import Movie, Category, Actor, Genre, Rating
from .forms import ReviewForm, RatingForm

class GenreYear():
    """Жанры и года выхода фильмов"""
    def get_genres(self):
        return Genre.objects.all()

    def get_years(self):
        return Movie.objects.filter(draft=False).values("year")

class MoviesView(GenreYear, ListView):
    """Список фильмов"""
    model = Movie
    queryset = Movie.objects.filter(draft=False)
    # template_name = "movies/movies.html"
    paginate_by = 5

    """Вместо кода ниже сделали movies/templatetags/movie_tag"""
    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args, **kwargs)
    #     context["categories"] = Category.objects.all()
    #     return context

"""Вместо кода ниже сделали класс MoviesView(ListView)"""
# class MoviesView(View):
    # def get(self, request):
    #     movies = Movie.objects.all()
    #     return render(request, 'movies/movies.html', {'movie_list': movies})

class MovieDetailView(GenreYear, DetailView):
    """Полное описание фильма"""
    model = Movie
    queryset = Movie.objects.filter(draft=False)
    slug_field = "url"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["star_form"] = RatingForm()
        return context


    """Вместо кода ниже сделали movies/templatetags/movie_tag"""
    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args, **kwargs)
    #     context["categories"] = Category.objects.all()
    #     return context
"""Вместо кода ниже сделали класс MovieDetailView(DetailView)"""
# class MovieDetailView(View):
#     """Полное описание фильма"""
#     def get(self, request, slug):
#         movie = Movie.objects.get(url=slug
#         return render(request, "movies/movie_detail.html", {'movie': movie})

class AddReview(View):
    """Отзывы"""
    def post(self, request, pk):
        form = ReviewForm(request.POST)
        movie = Movie.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get("parent", None):
                form.parent_id = int(request.POST.get("parent"))
            form.movie = movie
            form.save()
        return redirect(movie.get_absolute_url())

class ActorView(GenreYear, DetailView):
    """Вывод информации об актёре"""
    model = Actor
    template_name = 'movies/actor.html'
    slug_field = "name"

class FilterMoviesView(GenreYear, ListView):
    """Фильтр фильмов (по Жанрам / Годам)"""
    paginate_by = 5

    def get_queryset(self):
        queryset = Movie.objects.filter(
            Q(year__in=self.request.GET.getlist("year")) |
            Q(genres__in=self.request.GET.getlist("genre"))
        ).distinct()
        print(f'{self.request.GET.getlist("year")=}\n{self.request.GET.getlist("genre")=}')
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["year"] = ''.join([f"year={x}&" for x in self.request.GET.getlist("year")])
        context["genre"] = ''.join([f"genre={x}&" for x in self.request.GET.getlist("genre")])
        return context

class JsonFilterMoviesView(ListView):
    """Фильтр фильмов в json"""
    def get_queryset(self):
        queryset = Movie.objects.filter(
            Q(year__in=self.request.GET.getlist("year")) |
            Q(genres__in=self.request.GET.getlist("genre"))
        ).distinct().values("title", "tagline", "url", "poster")
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = list(self.get_queryset())
        return JsonResponse({"movies": queryset}, safe=False)


class AddStarRating(View):
    """Добавление рейтинга фильму"""
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                movie_id=int(request.POST.get("movie")),
                defaults={'star_id': int(request.POST.get("star"))}
            )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)

class Search(ListView):
    """Поиск фильмов"""
    paginate_by = 3
    def get_queryset(self):
        return Movie.objects.filter(title__icontains=self.request.GET.get("q"))
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["q"] = f'q={self.request.GET.get("q")}&'
        return context
