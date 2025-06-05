from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
import json

# serializers
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and isinstance(response.data, dict):
        # Extract all error messages into a plain string
        plain_errors = []
        for field, messages in response.data.items():
            if isinstance(messages, list):
                for message in messages:
                    plain_errors.append(f"({field}) " + str(message))
            else:
                plain_errors.append(f"({field}) " + str(messages))

        response.data = {"error": "\n".join(plain_errors)}

    return response


class CustomPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate(self, data):
        # Check if the new passwords match
        if data["new_password1"] != data["new_password2"]:
            raise serializers.ValidationError("The two new passwords must match.")
        return data

    def validate_old_password(self, value):
        # Validate the old password against the current password
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
