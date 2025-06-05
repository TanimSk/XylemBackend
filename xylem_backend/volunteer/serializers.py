from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from volunteer.models import Volunteer

# Custom Registration
class VolunteerRegistrationSerializer(RegisterSerializer):
    volunteer = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )
    name = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=True, max_length=255)
    phone = serializers.CharField(required=False, max_length=20, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    def get_attribute(self, instance):
        data = super(VolunteerRegistrationSerializer, self).get_cleaned_data()
        extra_data = {
            "name": data.get("name"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "address": data.get("address"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        }
        data.update(extra_data)
        return data
    
    def save(self, request):
        user = super(VolunteerRegistrationSerializer, self).save(request)
        user.is_volunteer = True
        user.save()
        # Create the Volunteer instance
        volunteer = Volunteer.objects.create(
            volunteer=user,
            name=self.validated_data.get("name"),
            email=self.validated_data.get("email"),
            phone=self.validated_data.get("phone"),
            address=self.validated_data.get("address"),
            latitude=self.validated_data.get("latitude"),
            longitude=self.validated_data.get("longitude"),
        )
        return volunteer
