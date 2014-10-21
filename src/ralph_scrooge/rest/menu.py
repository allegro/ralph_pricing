from rest_framework.views import APIView
from rest_framework.response import Response


class Menu(APIView):
    def get(self, request, format=None):
        return Response([
            {
                'name': 'Components',
                'href': '#/components/',
                'leftMenu': ['services'],
            },
            {
                'name': 'Allocations',
                'href': '#/allocation/client/',
                'leftMenu': ['services', 'teams'],
            }
        ])
