import requests
from django.core.management.base import BaseCommand

from pokedex.models import EvolutionChain, Pokemon, Region, Type

POKEAPI_BASE = "https://pokeapi.co/api/v2"

ROMAN_TO_NUM = {
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5,
    "vi": 6, "vii": 7, "viii": 8, "ix": 9,
}

REGION_MAP = {
    1: "Kanto",
    2: "Johto",
    3: "Hoenn",
    4: "Sinnoh",
    5: "Unova",
    6: "Kalos",
    7: "Alola",
    8: "Galar",
    9: "Paldea",
}

TYPE_COLORS = {
    "normal": "#A8A77A",
    "fire": "#EE8130",
    "water": "#6390F0",
    "electric": "#F7D02C",
    "grass": "#7AC74C",
    "ice": "#96D9D6",
    "fighting": "#C22E28",
    "poison": "#A33EA1",
    "ground": "#E2BF65",
    "flying": "#A98FF3",
    "psychic": "#F95587",
    "bug": "#A6B91A",
    "rock": "#B6A136",
    "ghost": "#735797",
    "dragon": "#6F35FC",
    "dark": "#705746",
    "steel": "#B7B7CE",
    "fairy": "#D685AD",
}


class Command(BaseCommand):
    help = "Importa Pokémon, tipos, regiones y cadenas evolutivas desde PokeAPI"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit number of Pokémon to import (for testing)",
        )

    def handle(self, *args, **options):
        limit = options.get("limit")
        self.import_types()
        self.import_regions()
        self.import_pokemon(limit)
        self.stdout.write(self.style.SUCCESS("¡Importación completada exitosamente!"))

    def import_types(self):
        self.stdout.write("Importando tipos...")
        response = requests.get(f"{POKEAPI_BASE}/type", timeout=30)
        response.raise_for_status()
        data = response.json()

        for type_data in data["results"]:
            type_name = type_data["name"]
            color = TYPE_COLORS.get(type_name, "#999999")
            Type.objects.update_or_create(name=type_name, defaults={"color": color})
            self.stdout.write(f"  Tipo: {type_name} ({color})")

    def import_regions(self):
        self.stdout.write("Importando regiones...")
        for gen, name in REGION_MAP.items():
            Region.objects.update_or_create(
                name=name, defaults={"generation_number": gen}
            )
            self.stdout.write(f"  Región: {name} (Gen {gen})")

    def import_pokemon(self, limit):
        self.stdout.write("Obteniendo lista de Pokémon desde PokeAPI...")
        response = requests.get(
            f"{POKEAPI_BASE}/pokemon?limit={limit or 100000}&offset=0", timeout=60
        )
        response.raise_for_status()
        pokemon_list = response.json()["results"]
        self.stdout.write(f"  Total: {len(pokemon_list)} Pokémon")

        for idx, pokemon_entry in enumerate(pokemon_list, 1):
            self.import_single_pokemon(pokemon_entry["url"])
            if idx % 50 == 0:
                self.stdout.write(f"  Progreso: {idx}/{len(pokemon_list)}")

    def import_single_pokemon(self, url):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            pokemon_id = data["id"]
            name = data["name"]
            image_url = data["sprites"].get("other", {}).get(
                "official-artwork", {}
            ).get("front_default") or data["sprites"].get("front_default") or ""

            height = data.get("height", 0)
            weight = data.get("weight", 0)

            species_url = data["species"]["url"]
            species_response = requests.get(species_url, timeout=30)
            species_response.raise_for_status()
            species_data = species_response.json()

            generation_url = species_data.get("generation", {}).get("url", "")
            region = None
            if generation_url:
                gen_response = requests.get(generation_url, timeout=30)
                gen_response.raise_for_status()
                gen_data = gen_response.json()
                gen_name = gen_data.get("name", "")
                gen_roman = gen_name.replace("generation-", "")
                gen_number = ROMAN_TO_NUM.get(gen_roman)
                if gen_number and gen_number in REGION_MAP:
                    region = Region.objects.filter(
                        name=REGION_MAP[gen_number]
                    ).first()

            chain_url = species_data.get("evolution_chain", {}).get("url", "")
            evolution_chain = None
            if chain_url:
                chain_api_id = int(chain_url.strip("/").split("/")[-1])
                chain_obj, _ = EvolutionChain.objects.get_or_create(
                    api_id=chain_api_id,
                    defaults={"chain_data": {}},
                )
                evolution_chain = chain_obj
                if not chain_obj.chain_data:
                    try:
                        chain_response = requests.get(chain_url, timeout=30)
                        chain_response.raise_for_status()
                        chain_obj.chain_data = chain_response.json()
                        chain_obj.save()
                    except requests.RequestException:
                        pass

            evolves_from_species = species_data.get("evolves_from_species")
            evolves_from = None
            if evolves_from_species:
                evo_name = evolves_from_species["name"]
                evolves_from = Pokemon.objects.filter(name=evo_name).first()

            pokemon, created = Pokemon.objects.update_or_create(
                pokedex_number=pokemon_id,
                defaults={
                    "name": name,
                    "image_url": image_url,
                    "region": region,
                    "evolution_chain": evolution_chain,
                    "evolves_from": evolves_from,
                    "height": height,
                    "weight": weight,
                },
            )

            for type_entry in data["types"]:
                type_name = type_entry["type"]["name"]
                try:
                    poke_type = Type.objects.get(name=type_name)
                    pokemon.types.add(poke_type)
                except Type.DoesNotExist:
                    pass

        except requests.RequestException as e:
            self.stdout.write(
                self.style.WARNING(f"  Error con Pokémon {url}: {e}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(
                    f"  Error inesperado con Pokémon {url}: {e}"
                )
            )
