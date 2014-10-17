from rest_framework.views import APIView
from rest_framework.response import Response


class Menu(APIView):
    def get(self, request, format=None):
        return Response([
            {
                'name': 'Components',
                'href': '#/components/',
            },
            {
                'name': 'Allocations',
                'href': '#/allocation/client/',
            }
        ])
