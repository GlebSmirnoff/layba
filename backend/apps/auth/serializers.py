from rest_framework import serializers
import re

E164_RE = re.compile(r"^\+[1-9]\d{6,14}$")

class E164Field(serializers.CharField):
    def to_internal_value(self, data):
        val = super().to_internal_value(data).strip()
        if not E164_RE.match(val):
            raise serializers.ValidationError("Phone must be in E.164 format")
        return val

class PhoneSendCodeIn(serializers.Serializer):
    phone = E164Field()
    method = serializers.ChoiceField(choices=["sms", "call"])

class PhoneVerifyIn(serializers.Serializer):
    phone = E164Field()
    code = serializers.CharField(required=False, allow_blank=True)
    last4 = serializers.CharField(required=False, allow_blank=True, max_length=4)

    def validate(self, attrs):
        if not attrs.get("code") and not attrs.get("last4"):
            raise serializers.ValidationError("Either 'code' or 'last4' must be provided")
        if attrs.get("code") and attrs.get("last4"):
            raise serializers.ValidationError("Provide only one of 'code' or 'last4'")
        return attrs

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

class ErrorSerializer(serializers.Serializer):
    """
    {
      "code": "string",
      "message": "string",
      "details": { ... },
      "request_id": "uuid-or-empty"
    }
    """
    code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
    request_id = serializers.CharField(required=False, allow_blank=True)