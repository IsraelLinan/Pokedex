from django.shortcuts import render
import urllib.request   
import json
from http import HTTPStatus
from urllib.error import HTTPError, URLError

# Create your views here.
def index(request):
    try:
        if request.method == 'POST':
            pokemon = request.POST['pokemon'].lower()
            pokemon = pokemon.replace(" ", "%20")
            url_pokeapi = urllib.request.Request(f'https://pokeapi.co/api/v2/pokemon/{pokemon}')
            url_pokeapi.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
            
            source = urllib.request.urlopen(url_pokeapi).read()
            
            list_of_data = json.loads(source)
            
            # Altura de decímetros a metros
            height_obtained = (float(list_of_data['height']) * 0.1)
            height_rounded = round(height_obtained, 2)

            # Peso de hectogramos a kilogramos
            weight_obtained = (float(list_of_data['weight']) * 0.1)
            weight_rounded = round(weight_obtained, 2)
            
            artwork = list_of_data['sprites']['other']['official-artwork']['front_default']
            types = [t['type']['name'] for t in list_of_data.get('types', [])]
            
            data = {
                "numero": str(list_of_data['id']),
                "nombre": str(list_of_data['name']).capitalize(),
                "altura": str(height_rounded) + " metros",
                "peso": str(weight_rounded) + " kg",
                "sprite": str(list_of_data['sprites']['front_default']),
                "artwork": artwork,
                "tipos": types,
            }
            
            print(data)
            
        else:
            data = {}
            
        return render(request, 'main/index.html', data)
    except HTTPError as e:
        if e.code == 404:
            return render(request, 'main/404.html')
        
            