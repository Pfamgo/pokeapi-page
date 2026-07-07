from django.contrib import admin

from .models import EvolutionChain, Pokemon, Region, Type


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["name", "generation_number"]
    search_fields = ["name"]


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ["name", "color"]
    search_fields = ["name"]


@admin.register(EvolutionChain)
class EvolutionChainAdmin(admin.ModelAdmin):
    list_display = ["id"]
    readonly_fields = ["chain_data"]


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ["pokedex_number", "name", "region"]
    list_filter = ["region", "types"]
    search_fields = ["name", "pokedex_number"]
    filter_horizontal = ["types"]
