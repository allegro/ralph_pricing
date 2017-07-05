from rest_framework.pagination import LimitOffsetPagination


class ScroogeLimitOffsetPagination(LimitOffsetPagination):
    # cannot set it through rest framework settings (PAGE_SIZE) - it would
    # break existing endpoints (add count, next and results to response json)
    default_limit = 50
