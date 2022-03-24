from rest_framework import serializers
from user.models   import *


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = "__all__"


