import requests
from utils import Urls, save_json, load_json, get_file_path, File
import os



def has_saved(file: File, *args: str) -> bool:
    file_path = get_file_path(file, *args)
    return os.path.exists(file_path)

class Categories:

    def __init__(self):
        self.url = Urls.categories()
        self.file = "categories"

    def load(self):
        data = requests.get(self.url).json()
        data = data["categories"]
        data = {c["name"]: c["id"] for c in data}
        return data

    def get_all(self):
        if has_saved(self.file):
            return load_json(self.file)
        return self.load()

    def get_category(self, id: int | None = None, name: str | None = None):
        
        if has_saved(self.file):
            data = load_json(self.file)
        else: 
            data = self.load()
        
        if id is not None:
            return Category(id)
        return Category(data[name])
            
    
class Category:
    
    def __init__(self, id):
        self.id = id

def get_categories():

    if has_saved("categories"):
        return load_json("categories")
    
    url = Urls.categories()
    data = requests.get(url).json()
    data = data["categories"]
    data = {c["name"]: c["id"] for c in data}
    return data

def get_category(data_categorys: dict, category: str):

    if has_saved("category", category):
        return load_json("category", category)
    
    url = Urls.category(data_categorys[category])
    data = requests.get(url).json()
    data = data["groups"][0]["uniqueTournaments"]
    data = {c["name"]: c["id"] for c in data}
    return data

def get_tournament(data_category: dict, category: str, tournament: str):

    if has_saved("tournament", category, tournament):
        return load_json("tournament", category, tournament)

    url = Urls.tournament(data_category[tournament])
    data = requests.get(url).json()
    data = data["seasons"]
    filter_data = {}
    for season in data:
        del season["editor"]
        name = season["name"]
        filter_data[name] = season

    return filter_data

def get_season(data_tournament, data_seasons, tournament, year):
    
    for t in data_tournament:
        if t == tournament:
            id_tournament = data_tournament[t]

    for s in data_seasons:
        if data_seasons[s]["year"] == year:
            id_season = data_seasons[s]["id"]

    url = Urls.season(id_tournament, id_season, 1)
    data = requests.get(url).json()
    data = data["events"]
    for i,e in enumerate(data):
        e = {
            "home": e["homeTeam"]["name"],
            "away": e["awayTeam"]["name"],
            "homeScore": e["homeScore"],
            "awayScore": e["awayScore"],
            "id": e["awayTeam"]["id"]
        }
        del e["homeScore"]["display"]
        del e["homeScore"]["current"]
        del e["awayScore"]["display"]
        del e["awayScore"]["current"]
        data[i] = e
        
    return data


def get_season_id(data_tournaments, season):
    for t in data_tournaments:
        print(t)
        if t == season:
            return data_tournaments[t]["id"]



CATEGORY = 'Brazil'
TOURNAMENT = "Brasileirão Série A"
SEASON = "Brasileiro Serie A 2024"
YEAR = "2024"


data = get_categories()
save_json(data, "categories", update=False)

data = get_category(data, CATEGORY)
save_json(data, "category", CATEGORY, update=False)

data_seasons = get_tournament(data, CATEGORY, TOURNAMENT)
save_json(data_seasons, "tournament", CATEGORY, TOURNAMENT, update=False)


data = get_season(data, data_seasons, TOURNAMENT, YEAR)
save_json(data, "season", CATEGORY, SEASON, update=False)