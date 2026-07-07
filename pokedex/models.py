from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)
    generation_number = models.PositiveIntegerField(unique=True)

    class Meta:
        verbose_name = "Región"
        verbose_name_plural = "Regiones"
        ordering = ["generation_number"]

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, help_text="Hex color for badge (e.g. #FF0000)")

    class Meta:
        verbose_name = "Tipo"
        verbose_name_plural = "Tipos"
        ordering = ["name"]

    def __str__(self):
        return self.name


class EvolutionChain(models.Model):
    api_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    chain_data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Cadena Evolutiva"
        verbose_name_plural = "Cadenas Evolutivas"

    def __str__(self):
        return f"Evolution Chain #{self.api_id or self.id}"


class Pokemon(models.Model):
    pokedex_number = models.PositiveIntegerField(unique=True, verbose_name="Número Pokédex")
    name = models.CharField(max_length=100)
    image_url = models.URLField(max_length=500, blank=True, default="")
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, blank=True, related_name="pokemon"
    )
    types = models.ManyToManyField(Type, related_name="pokemon")
    evolves_from = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evolutions",
    )
    evolution_chain = models.ForeignKey(
        EvolutionChain,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pokemon",
    )
    height = models.PositiveIntegerField(default=0, help_text="Height in decimeters")
    weight = models.PositiveIntegerField(default=0, help_text="Weight in hectograms")

    class Meta:
        verbose_name = "Pokémon"
        verbose_name_plural = "Pokémon"
        ordering = ["pokedex_number"]

    def __str__(self):
        return f"#{self.pokedex_number:04d} {self.name}"
