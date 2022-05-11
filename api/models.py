from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model): # Profileモデル
    user_prof = models.OneToOneField(
        User,    # user_prof属性をUserと結びつけている。
        related_name='profile',     # 逆参照の名称をprofileに変更。
        on_delete=models.CASCADE    #
    )
    # friendsフィールド
    friends = models.ManyToManyField(
        User,
        related_name='profiles_friends',    # Userモデルからfriend関係にあるUserにアクセスできる。
        blank=True
    )
    friend_requests = models.ManyToManyField(
        User,
        related_name='profiles_friend_requests',
        blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_prof.username


class Message(models.Model):
    message = models.CharField(max_length=140)
    # DM送付User
    sender = models.ForeignKey(
        User,
        related_name='message_sender',  #
        on_delete=models.CASCADE
    )
    # DM受信側User
    receiver = models.ForeignKey(
        User,
        related_name='message_receiver',    #
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.id)