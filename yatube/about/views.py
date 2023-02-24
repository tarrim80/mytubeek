from django.views.generic import DetailView, ListView

from about.models import About, Tech


class AboutAuthorView(DetailView):
    model = About
    template_name = "about/author.html"


class AboutTechView(ListView):
    model = Tech
    template_name = "about/tech.html"
