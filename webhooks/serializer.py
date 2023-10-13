from rest_framework.serializers import ModelSerializer
from webhooks.models import WebhookEvents


class WebhookEventsSerializer(ModelSerializer):
    class Meta:
        model = WebhookEvents
        fields = "__all__"
