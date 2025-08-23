# views.py
from django.shortcuts import render
import urllib.request
import urllib.parse
import json
import logging
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)

def index(request):
    data = {}
    try:
        if request.method == 'POST':
            # Prioridad: acción de navegación -> campo pokemon
            action = request.POST.get('action')
            current_id = request.POST.get('current_id', '').strip()
            user_input = request.POST.get('pokemon', '').strip()

            # Si viene acción de navegación y current_id es entero -> navegar
            if action in ('prev', 'next') and current_id.isdigit():
                cid = int(current_id)
                new_id = max(1, cid - 1) if action == 'prev' else cid + 1
                lookup = str(new_id)  # buscamos por ID
                data['query'] = lookup
            else:
                # Si el usuario escribió algo (nombre o id), usamos eso
                if user_input == '':
                    data['error'] = "Escribe el nombre o el ID de un Pokémon."
                    return render(request, 'main/index.html', data)
                lookup = user_input.lower()
                data['query'] = user_input

            # Codificar para la URL (maneja espacios, acentos)
            lookup_encoded = urllib.parse.quote_plus(lookup)
            url = f'https://pokeapi.co/api/v2/pokemon/{lookup_encoded}'
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (compatible; PokedexApp)')

            with urllib.request.urlopen(req, timeout=10) as resp:
                source = resp.read()

            list_of_data = json.loads(source)

            # Altura (decímetros -> metros) y peso (hectogramos -> kg)
            height = round(float(list_of_data.get('height', 0)) * 0.1, 2)
            weight = round(float(list_of_data.get('weight', 0)) * 0.1, 2)

            sprites = list_of_data.get('sprites', {})
            artwork = sprites.get('other', {}).get('official-artwork', {}).get('front_default')
            sprite = sprites.get('front_default')

            # Tipos capitalizados
            types = [t['type']['name'].capitalize() for t in list_of_data.get('types', [])]

            # === Estadísticas base ===
            # Mapeo a etiquetas en español
            name_map = {
                'hp': 'PS',
                'attack': 'Ataque',
                'defense': 'Defensa',
                'special-attack': 'At. Esp.',
                'special-defense': 'Def. Esp.',
                'speed': 'Velocidad',
            }

            raw_stats = list_of_data.get('stats', [])
            processed_stats = []
            total_stats = 0
            for s in raw_stats:
                key = s.get('stat', {}).get('name', '')
                label = name_map.get(key, key.replace('-', ' ').title())
                value = int(s.get('base_stat', 0))
                # Porcentaje contra 255 (máximo histórico de base stats)
                percent = max(0, min(100, round((value / 255) * 100)))
                processed_stats.append({
                    "key": key,
                    "label": label,
                    "value": value,
                    "percent": percent,
                })
                total_stats += value

            numero = str(list_of_data.get('id', ''))

            data.update({
                "numero": numero,
                "nombre": str(list_of_data.get('name', '')).capitalize(),
                "altura": f"{height} metros",
                "peso": f"{weight} kg",
                "sprite": sprite,
                "artwork": artwork,
                "tipos": types,
                "stats": processed_stats,
                "total": total_stats,
                # mantenemos query para rellenar el input
                "query": data.get('query', numero),
            })

        # GET o POST procesado -> render
        return render(request, 'main/index.html', data)

    except HTTPError as e:
        logger.exception("HTTPError consultando PokeAPI")
        if e.code == 404:
            data['error'] = "Pokémon no encontrado. Revisa el nombre o ID."
        else:
            data['error'] = f"Error HTTP al consultar la API (código {e.code})."
        return render(request, 'main/index.html', data)

    except URLError:
        logger.exception("URLError consultando PokeAPI")
        data['error'] = "Error de conexión: no se pudo contactar con PokeAPI."
        return render(request, 'main/index.html', data)

    except Exception:
        logger.exception("Error inesperado en la vista index")
        data['error'] = "Ocurrió un error inesperado. Revisa los logs del servidor."
        return render(request, 'main/index.html', data)


        
            