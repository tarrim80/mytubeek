from django.views.generic.base import TemplateView
from django.views.generic import ListView

from about.models import Tech


class AboutAuthorView(TemplateView):
    template_name = "about/author.html"


class AboutTechView(ListView):
    model = Tech
    template_name = "about/tech.html"
