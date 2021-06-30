from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from messaging.api.serializers import NotificationSerializer, NotificationTemplateSerializer
from messaging.models import Notification, NotificationTemplate
from messaging.utils import create_user_notifications, create_user_notifications_all_channel


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.none()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(
            notification_type=Notification.Types.PUSH, user=self.request.user,
            when__lt=timezone.now(), status=Notification.Statuses.SENT
        )
        return qs


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    # permission_classes = [IsAuthenticated]


class SendMessage(APIView):

    def post(self, request):

        template_id = request.GET.get("template_id", None)
        recipient = request.GET.get("recipient", None)
        language = request.GET.get("language", None)
        channel = request.GET.get("channel", None)
        try:
            data = request.data.dict()
        except:
            return Response({"error_en": "Please send validate format"}, status=status.HTTP_400_BAD_REQUEST)

        notification = create_user_notifications_all_channel(template_id=template_id, customer=None, data=data,
                                                             recipient=recipient, language=language, channel=channel)

        if notification:
            return Response({"message": "Message sent successfully"})

        else:
            return Response({"error_en": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
