from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from volunteer.models import Volunteer


# Custom Registration
class VolunteerRegistrationSerializer(RegisterSerializer):
    volunteer = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )  # by default allow_null = False
    name = serializers.CharField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    def get_cleaned_data(self):
        data = super(VolunteerRegistrationSerializer, self).get_cleaned_data()
        extra_data = {
            "name": self.validated_data.get("name"),
            "phone": self.validated_data.get("phone"),
            "address": self.validated_data.get("address"),
            "latitude": self.validated_data.get("latitude"),
            "longitude": self.validated_data.get("longitude"),
        }
        data.update(extra_data)
        return data

    def save(self, request):
        user = super(VolunteerRegistrationSerializer, self).save(request)
        user.is_volunteer = True
        user.first_name = self.cleaned_data.get("name")
        user.save()
        user_instance = Volunteer(
            volunteer=user,
            name=self.cleaned_data.get("name"),
            phone=self.cleaned_data.get("phone"),
            address=self.cleaned_data.get("address"),
            latitude=self.cleaned_data.get("latitude"),
            longitude=self.cleaned_data.get("longitude"),
        )
        user_instance.save()
        return user
