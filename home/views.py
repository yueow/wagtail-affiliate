import os
from django.views.generic.base import TemplateView

# Robots.txt
class RobotsView(TemplateView):
    content_type = 'text/plain'

    def get_template_names(self):
        return 'robots.txt'