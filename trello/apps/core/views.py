from django.shortcuts import render

# Create your views here.

from django.views import View
from django.template import Template

class HomeVeiw(View):
    def get(self, request):
        return render(request, 'core/home.html')