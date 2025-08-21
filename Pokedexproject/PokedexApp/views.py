# views.py (reemplaza el contenido actual por este)
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
                if action == 'prev':
                    new_id = max(1, cid - 1)
                else:
                    new_id = cid + 1
                lookup = str(new_id)  # buscarmos por ID
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

            artwork = list_of_data.get('sprites', {}) \
                                 .get('other', {}) \
                                 .get('official-artwork', {}) \
                                 .get('front_default')
            sprite = list_of_data.get('sprites', {}).get('front_default')

            # Tipos capitalizados
            types = [t['type']['name'].capitalize() for t in list_of_data.get('types', [])]

            numero = str(list_of_data.get('id', ''))

            data.update({
                "numero": numero,
                "nombre": str(list_of_data.get('name', '')).capitalize(),
                "altura": f"{height} metros",
                "peso": f"{weight} kg",
                "sprite": sprite,
                "artwork": artwork,
                "tipos": types,
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

        
            