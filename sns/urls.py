from django.contrib import admin
from django.urls import path

from graphene_django.views import GraphQLView
from sns.schema import schema
from django.views.decorators.csrf import csrf_exempt


''' GraphQLのエンドポイントを作成 : GraphQLなので1つだけで済む。 '''
urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),

]
