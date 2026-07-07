from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm, SearchForm
from .models import Pokemon


def home(request):
    form = SearchForm(request.GET or None)
    pokemon_list = Pokemon.objects.select_related("region").prefetch_related("types").all()

    if form.is_valid():
        q = form.cleaned_data.get("q")
        type_filter = form.cleaned_data.get("type")
        region_filter = form.cleaned_data.get("region")

        if q:
            pokemon_list = pokemon_list.filter(
                models.Q(name__icontains=q) | models.Q(pokedex_number__icontains=q)
            )
        if type_filter:
            pokemon_list = pokemon_list.filter(types=type_filter)
        if region_filter:
            pokemon_list = pokemon_list.filter(region=region_filter)

    context = {
        "pokemon_list": pokemon_list,
        "form": form,
    }
    return render(request, "pokedex/home.html", context)


def pokemon_detail(request, pokemon_id):
    pokemon = Pokemon.objects.select_related("region", "evolution_chain", "evolves_from").prefetch_related(
        "types", "evolutions"
    ).get(pk=pokemon_id)

    evolution_pokemon = []
    if pokemon.evolution_chain:
        chain_pokemon = Pokemon.objects.filter(evolution_chain=pokemon.evolution_chain).order_by("pokedex_number")
        evolution_pokemon = list(chain_pokemon)

    context = {
        "pokemon": pokemon,
        "evolution_pokemon": evolution_pokemon,
    }
    return render(request, "pokedex/pokemon_detail.html", context)


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "pokedex/register.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
    else:
        form = LoginForm()

    return render(request, "pokedex/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("home")


@login_required
def profile(request):
    return render(request, "pokedex/profile.html")
