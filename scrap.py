import requests
from utils import Urls, save_json, get_file_path


def get_categorys():
    url = Urls.CATEGORIES
    data = requests.get(url).json()
    data = data["categories"]
    data = {
        c["name"]: c["id"] for c in data
    }
    return data

def get_category(data_categorys, category):

    url = Urls.CATEGORY.format(data_categorys[category])
    data = requests.get(url).json()
    data = data["groups"][0]["uniqueTournaments"]
    data = {c["name"]: c["id"] for c in data}
    return data

def get_tournament(data_category, tournament):
    url = Urls.TOURNAMENT.format(data_category[tournament])
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

    url = Urls.SEASON.format(id_tournament, id_season, 1)
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


data = get_categorys()
save_json(data, "categories", update=False)

data = get_category(data, CATEGORY)
save_json(data, "category", CATEGORY, update=False)

data_seasons = get_tournament(data, TOURNAMENT)
save_json(data, "tournament", CATEGORY, TOURNAMENT, update=False)


data = get_season(data, data_seasons, TOURNAMENT, YEAR)
save_json(data, "season", CATEGORY, TOURNAMENT, update=False)