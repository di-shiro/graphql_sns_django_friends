import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
import graphql_jwt
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from graphql_jwt.decorators import login_required
from .models import Profile, Message
from graphql_relay import from_global_id


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            'username': ['exact', 'icontains'],
        }
        interfaces = (relay.Node,)

class ProfileNode(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = {
            'user_prof__username': ['icontains'],
        }
        interfaces = (relay.Node,)

class MessageNode(DjangoObjectType):    # Direct Message
    class Meta:
        model = Message
        filter_fields = {
            'sender': ['exact'],
            'receiver': ['exact'],
        }
        interfaces = (relay.Node,)

''' 新規Userを作成 '''
class CreateUserMutation(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    user = graphene.Field(UserNode)

    def mutate_and_get_payload(root, info, **input):
        user = User(
            username=input.get('username'),
            email=input.get('email'),
        )
        user.set_password(input.get('password'))
        user.save()

        return CreateUserMutation(user=user)

class MessageCreateMutation(relay.ClientIDMutation):    # Direct Massage
    class Input:    # React側から受け取るデータ
        message = graphene.String(required=True)    # DMの文章
        receiver = graphene.ID(required=True)       # DMを受け取る側のUserのID

    message = graphene.Field(MessageNode)   # Messageのフィールドを作成

    @login_required     # Messageの具体的な処理
    def mutation_and_get_payload(root, info, **input):
        message = Message(
            message=input.get('message'),
            sender_id=info.context.user.id,     # ログインUserのID
            receiver_id=from_global_id(input.get('receiver'))[1]    # 上の class Input: で受け取ったDM受信相手UserのID
        )
        message.save()
        return MessageCreateMutation(message=message)


''' 新規Profileを作成 '''
class ProfileCreateMutation(relay.ClientIDMutation):
    profile = graphene.Field(ProfileNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        profile = Profile(
            user_prof_id=info.context.user.id,
        )
        profile.save()
        return ProfileCreateMutation(profile=profile)


''' Update '''
class ProfileUpdateMutation(relay.ClientIDMutation):
    class Input: # React側でGraphQLクエリのInputに指定する項目を設定
        id = graphene.ID(required=True)
        friends = graphene.List(graphene.ID)
        friend_requests = graphene.List(graphene.ID)

    profile = graphene.Field(ProfileNode)

    # Updateの具体的な処理
    @login_required
    def mutate_and_get_payload(root, info, **input):
        # DBからReact側で指定したUserIDのデータを取得
        profile = Profile.objects.get(id=from_global_id(input.get('id'))[1])
        # React側でのGraphQLクエリのInputのfriendsに何か入っている場合、そのUserIDリストを配列に展開
        if input.get('friends') is not None:
            friends_set = []
            for tempFriend in input.get('friends'):
                friends_id = from_global_id(tempFriend)[1]     # IDが文字列なので、Djangoで扱えるように数字に変換。
                # friens_idに対応したUserオブジェクトを取得
                friends_object = User.objects.get(id=friends_id)
                friends_set.append(friends_object)      # Userオブジェクトの配列を作成
            profile.friends.set(friends_set)        # React側からInputで受け取った friendsリストでDBを更新

        ''' React側から friend_requests でFriend申請を受けた場合の処理 '''
        if input.get('friend_requests') is not None:
            friend_requests_set = []
            for tempFriend in input.get('friend_requests'):
                friend_requests_id = from_global_id(tempFriend)[1]
                friend_requests_object = User.objects.get(id=friend_requests_id)
                friend_requests_set.append(friend_requests_object)
            profile.friend_requests.set(friend_requests_set)    # React側から受け取ったfriend_requestsリストでDBを更新
        profile.save()
        return ProfileUpdateMutation(profile=profile)


''' Mutationを定義して使えるようにしておく '''
class Mutation(graphene.AbstractType):
    create_user = CreateUserMutation.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    create_profile = ProfileCreateMutation.Field()
    update_profile = ProfileUpdateMutation.Field()
    create_message = MessageCreateMutation.Field()      # Direct Message

''' Queryを定義して使えるようにしておく '''
class Query(graphene.ObjectType):
    profile = graphene.Field(ProfileNode)
    all_users = DjangoFilterConnectionField(UserNode)
    all_profiles = DjangoFilterConnectionField(ProfileNode)
    all_messages = DjangoFilterConnectionField(MessageNode)     # Direct Message

    ''' Resolverの関数: 上記４つの具体的な処理。 '''
    @login_required
    def resolve_profile(self, info, **kwargs):
        return Profile.objects.get(user_prof=info.context.user.id)

    @login_required
    def resolve_all_users(self, info, **kwargs):
        return User.objects.all()

    @login_required
    def resolve_all_profiles(self, info, **kwargs):
        return Profile.objects.all()

    @login_required
    def resolve_all_messages(self, info, **kwargs):
        return Message.objects.all()



