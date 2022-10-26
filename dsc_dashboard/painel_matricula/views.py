from django.shortcuts import render

def index(request):
    return render(request, 'painel_matricula/index.html')
