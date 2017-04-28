import operator

from django.db.models import Q
from dal import autocomplete


class ScroogeAutocomplete(autocomplete.Select2QuerySetView):
    search_fields = None

    def get_queryset(self):
        queryset = self.model._default_manager.all()
        if self.q:
            # split query string by whitespaces and apply filtering using
            # the folowing condition: each token from query string has to
            # occur in (at least) one of search fields
            # example:
            # query = 'john doe'
            # search_fields = ['first_name', 'last_name']
            # orm query: (Q(first_name='john') | Q(last_name='john')) & (Q(first_name='doe') | Q(last_name='doe'))  # noqa
            for token in self.q.split():
                filter_query = [
                    Q(**{'{}__icontains'.format(field): token})
                    for field in self.search_fields or ['name']
                ]
                queryset = queryset.filter(
                    reduce(operator.or_, filter_query)
                )
        return queryset
