from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def index(request):
    return render(request, 'dashboards/index.html')

@login_required
def app_1(request):
    context = {'dashboard_name' : 'app_1' }
    return render(request, 'dashboards/index.html', context)

@login_required
def app_2(request):
    context = {'dashboard_name' : 'app_2' }
    return render(request, 'dashboards/index.html', context)

@login_required
def app_3(request):
    context = {'dashboard_name' : 'app_3' }
    return render(request, 'dashboards/index.html', context)

@login_required
def app_4(request):
    context = {'dashboard_name' : 'app_4' }
    return render(request, 'dashboards/index.html', context)

@login_required
def app_5(request):
    context = {'dashboard_name' : 'app_5' }
    return render(request, 'dashboards/index.html', context)

@login_required
def app_6(request):
    context = {'dashboard_name' : 'app_6' }
    return render(request, 'dashboards/index.html', context)