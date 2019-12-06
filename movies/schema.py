import graphene
from graphene import relay
import graphql_jwt
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id

from movies.models import Movie, Director


class MovieType(DjangoObjectType):
    class Meta:
        model = Movie

    movie_age = graphene.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year = None

    def resolve_movie_age(self, info):
        return "Old movie" if self.year < 2000 else "New movie"


class DirectorType(DjangoObjectType):
    class Meta:
        model = Director


class MovieNode(DjangoObjectType):
    class Meta:
        model = Movie
        filter_fields = {
            "title": ["exact", "icontains", "istartswith"],
            "year": ["exact"],
        }
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    all_movies = DjangoFilterConnectionField(MovieNode)
    movie = relay.Node.Field(MovieNode)
    all_directors = graphene.List(DirectorType)

    @login_required
    def resolve_all_movies(self, info, **kwargs):
        title = kwargs.get("title", "")
        return Movie.objects.filter(title__icontains=title)

    def resolve_movie(self, info, **kwargs):
        pk = kwargs.get("id")
        if pk:
            return Movie.objects.get(pk=pk)

        return None

    def resolve_all_directors(self, info, **kwargs):
        return Director.objects.all()


class MovieCreateMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        year = graphene.Int(required=True)

    movie = graphene.Field(MovieType)

    def mutate(self, info, title, year):
        movie = Movie.objects.create(title=title, year=year)
        return MovieCreateMutation(movie=movie)


class MovieUpdateMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        year = graphene.Int()
        pk = graphene.ID(required=True)

    movie = graphene.Field(MovieType)

    def mutate(self, info, pk, title, year):
        movie = Movie.objects.get(pk=pk)
        if title is not None:
            movie.title = title
        if year is not None:
            movie.year = year
        movie.save()
        return MovieUpdateMutation(movie=movie)


class MovieUpdateMutationRelay(relay.ClientIDMutation):
    class Input:
        title = graphene.String()
        pk = graphene.ID(required=True)

    movie = graphene.Field(MovieType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, pk, title):
        movie = Movie.objects.get(pk=from_global_id(pk)[1])
        if title is not None:
            movie.title = title
        movie.save()
        return MovieUpdateMutation(movie=movie)


class MovieDeleteMutation(graphene.Mutation):
    class Arguments:
        pk = graphene.ID(required=True)

    movie = graphene.Field(MovieType)

    def mutate(self, info, pk):
        movie = Movie.objects.get(pk=pk)
        movie.delete()
        return MovieDeleteMutation(movie=None)


class Mutation:
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()

    create_movie = MovieCreateMutation.Field()
    update_movie = MovieUpdateMutation.Field()
    update_movie_relay = MovieUpdateMutationRelay.Field()
    delete_movie = MovieDeleteMutation.Field()
