import requests
import os
from utils import Urls, File, get_file_path, load_json, save_json, Base


class Categories(Base):

    def __init__(self):
        self.url = Urls.categories()
        self.locator = ("categories",)
        self.data = self.json()

    def _load(self):
        data = requests.get(self.url).json()
        data = data["categories"]
        data = {c["name"]: c["id"] for c in data}
        return data

    def json(self):
        if self.is_saved():
            return load_json(*self.locator)
        data = self._load()
        save_json(data, *self.locator)
        return data
    
    def get_category(self, id: int | None = None, name: str | None = None):
        
        if id is not None:
            return Category(id, self.get_name(id))
        return Category(self.get_id(name), name)
            
    
class Category(Base):
    
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.locator = ("category", self.name)
        self.data = self.json()

    def _load(self):
        url = Urls.category(self.id)
        data = requests.get(url).json()
        data = data["groups"][0]["uniqueTournaments"]
        data = {t["name"]: t["id"] for t in data}
        return data
    
    def get_tournament(self, id: int | None = None, name: str | None = None):
        if id is not None:
            return Tournament(id, self.get_name(id), self)
        return Tournament(self.get_id(name), name, self)
        

class Tournament(Base):

    def __init__(self, id: int, name: str, category: Category):
        self.id = id
        self.name = name
        self.category = category
        self.locator = ("tournament", self.category.name, self.name)
        self.data = self.json()

    def _load(self) -> dict:
        url = Urls.tournament(self.id)
        data = requests.get(url).json()
        data = data["seasons"]
        result = {}
        for s in data:
            result[s["name"]] = {
                "year": s["year"],
                "id": s["id"]
            }
        return result
    
    def get_name(self, id: int) -> str:
        for c in self.data:
            if self.data[c]["id"] == id:
                return c
        raise ValueError(f'id {id} não encontrado')

    
    def get_season(self, id: int | None = None, name: str | None = None):
        if id is not None:
            return Season(id, self.get_name(id), self.category, self)
        return Season(self.get_id(name), name, self.category, self)
    

class Season(Base):

    def __init__(self, id: int, name: str, category: Category, tournament: Tournament):
        self.id = id
        self.name = name
        self.category = category
        self.tournament = tournament
        self.locator = ("season", self.category.name, self.name)
        self.data = self.json()

    def _load(self):
        url = Urls.season(self.tournament.id, self.id, 1)
        data = requests.get(url).json()
        data = data["events"]

        filter_data = {}
        for match in data:
            
            home_team = match["homeTeam"]
            home_team = {
                "name": home_team["name"],
                "id": home_team["id"]
            }
            
            home_score = match["homeScore"]
            home_score = {
                "period1": home_score["period1"],
                "period2": home_score["period2"],
                "normaltime": home_score["normaltime"]
            }

            away_team = match["awayTeam"]
            away_team = {
                "name": away_team["name"],
                "id": away_team["id"]
            }
            away_score = match["awayScore"]
            away_score = {
                "period1": away_score["period1"],
                "period2": away_score["period2"],
                "normaltime": away_score["normaltime"]
            }

            match_name = f'{home_team["name"]} x {away_team["name"]}'
            filter_data[match_name] = {
                "homeTeam": home_team,
                "awayTeam": away_team,
                "homeScore": home_score,
                "awayScore": away_score
            }

        return filter_data