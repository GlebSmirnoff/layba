from rest_framework import serializers

class PhoneSendCodeIn(serializers.Serializer):
    phone = serializers.CharField()

class PhoneVerifyIn(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()

class EmailSendCodeIn(serializers.Serializer):
    email = serializers.EmailField()

class EmailConfirmIn(serializers.Serializer):
    code = serializers.CharField()

class SessionLoginIn(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    role = serializers.ChoiceField(choices=["user", "moderator"], required=False)

class SocialGoogleIn(serializers.Serializer):
    code = serializers.CharField()

class SocialFacebookIn(serializers.Serializer):
    access_token = serializers.CharField()

class SocialAppleIn(serializers.Serializer):
    id_token = serializers.CharField()
