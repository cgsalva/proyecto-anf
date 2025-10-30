from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def login_view(request):
    error = None
    if request.method == "GET":
        return render(request, 'login.html')
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")  # redirige al dashboard o página principal
        else:
            error = "Usuario o contraseña incorrectos"
    return render(request, "login.html", {"error": error})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    context = {'user': request.user}
    return render(request, 'dashboard.html', context)