import logging

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from ralph_scrooge.rest_api.private.serializers import SyncAcceptedCostsSerializer
from ralph_scrooge.sync.recipient import accepted_costs_handler


logger = logging.getLogger(__name__)


class SyncBetweenScroogesAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser)  # todo: superuser?

    def post(self, request, *args, **kwargs):
        serializer = SyncAcceptedCostsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        logger.debug('Sync accepted costs event data: {}'.format(
            serializer.validated_data
        ))
        accepted_costs_handler(
            data['date_from'], data['date_to'], data['type'], data['costs']
        )
        return Response({}, status=202)


