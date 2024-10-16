# myapp/serializers.py
from rest_framework import serializers

class NominateMemberSerializer(serializers.Serializer):
    members = serializers.ListField(
        child=serializers.IntegerField()
    )
