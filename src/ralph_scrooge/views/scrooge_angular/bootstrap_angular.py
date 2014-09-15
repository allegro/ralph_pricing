from django.views.generic import TemplateView


class BootstrapAngular(TemplateView):
    template_name = 'scrooge_angular/index.html'

    def get_context_data(self, **kwargs):
        context = {'version': __version__}
        return context