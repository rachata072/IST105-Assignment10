from django.shortcuts import render, redirect
from .forms import ContinentForm
import requests
import random
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# MongoDB connection (update with your MongoDB EC2 details)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['geo_weather']
history_collection = db['search_history']

# OpenWeatherMap API key
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

# View for continent selection form
def continent_form(request):
    if request.method == 'POST':
        form = ContinentForm(request.POST)
        if form.is_valid():
            continent = form.cleaned_data['continent']
            return redirect('search_results', continent=continent)
    else:
        form = ContinentForm()
    return render(request, 'continent_form.html', {'form': form})

# View for showing results and storing in MongoDB
def search_results(request, continent):
    # REST Countries API
    countries_url = f'https://restcountries.com/v3.1/region/{continent}'
    countries_response = requests.get(countries_url)
    if countries_response.status_code != 200:
        return render(request, 'search_results.html', {'error': 'Failed to fetch countries.'})
    countries_data = countries_response.json()
    # Pick 5 random countries with capitals
    valid_countries = [c for c in countries_data if c.get('capital')]
    if len(valid_countries) < 5:
        return render(request, 'search_results.html', {'error': 'Not enough countries with capitals found.'})
    selected_countries = random.sample(valid_countries, 5)
    results = []
    for country in selected_countries:
        country_name = country['name']['common']
        capital = country['capital'][0]
        population = country.get('population', 'N/A')
        latlng = country.get('latlng', ['N/A', 'N/A'])
        # OpenWeatherMap API
        weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={capital}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
        weather_response = requests.get(weather_url)
        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            temp = weather_data['main']['temp']
            description = weather_data['weather'][0]['description']
        else:
            temp = 'N/A'
            description = 'Weather not found'
        results.append({
            'country': country_name,
            'capital': capital,
            'population': population,
            'latlng': latlng,
            'temperature': temp,
            'weather': description,
        })
    # Store search in MongoDB
    history_collection.insert_one({
        'continent': continent,
        'results': results
    })
    return render(request, 'search_results.html', {'continent': continent, 'results': results})

# View for search history
def history(request):
    searches = list(history_collection.find().sort('_id', -1))
    return render(request, 'history.html', {'searches': searches})
