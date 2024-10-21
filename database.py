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
    
    def get_id(self, name: str) -> int:
        for c in self.data:
            if c == name:
                return self.data[c]["id"]
        raise ValueError(f"Nome {name} não encontrado")

    
    def get_season(self, id: int | None = None, name: str | None = None):
        if id is not None:
            return Season(id, self.get_name(id), self.category, self)
        return Season(self.get_id(name), name, self.category, self)
    
    def get_seasons(self, n: int):
        seasons = []
        for i,s in enumerate(self.data,1):
            seasons.append(Season(self.data[s]["id"], s, self.category, self))
            print(i)
            if i >= n:
                break
        return seasons
        

class Season(Base):

    def __init__(self, id: int, name: str, category: Category, tournament: Tournament):
        self.id = id
        self.name = name
        while '/' in self.name:
            self.name = self.name.replace('/', '-')
        self.category = category
        self.tournament = tournament
        self.locator = ("season", self.category.name, self.name)

    def load_round(self, round: int):
        url = Urls.season(self.tournament.id, self.id, round)
        data = requests.get(url).json()
        data = data["events"]


        filter_data = {}
        for match in data:
            
            home_team = match["homeTeam"]["name"]
            away_team = match["awayTeam"]["name"]
            match_name = f'{home_team} x {away_team}'

            status = match["status"]["type"]
            if status == 'notstarted':
                return None
            
            elif status != 'finished':
                continue
            
            home_data = {
                "name": home_team,
                "id": match["homeTeam"]["id"],
                "period1": match["homeScore"]["period1"],
                "period2": match["homeScore"]["period2"],
                "normaltime": match["homeScore"]["normaltime"]
            }

            away_data = {
                "name": away_team,
                "id": match["awayTeam"]["id"],
                "period1": match["awayScore"]["period1"],
                "period2": match["awayScore"]["period2"],
                "normaltime": match["awayScore"]["normaltime"]
            }

            filter_data[match_name] = {
                "home": home_data,
                "away": away_data,
                "status": status,
                "id": match["id"]
            }

        return filter_data
    
    def get_matches(self, rounds: list[int]):

        data = {}
        list_matches = []
        n = 1
        while n <= rounds:
            print(f'Rodada {n}   ', end='\n')
            round = self.load_round(n)
            if round is None:
                break
            for match in round:
                data[match] = round[match]
                list_matches.append(Match(round[match]))
            
            n += 1

        save_json(data, "season", self.category.name, self.name)
        return list_matches
    

class Team:
     
    def __init__(self, data: dict[str, str | int]):
        self.name = data["name"]
        self.id = data["id"]
        self.period1 = data["period1"]
        self.period2 = data["period2"]
        self.score = data["normaltime"]

class Match:

    def __init__(self, data: dict[str, dict]):
        self.id = data["id"]
        self.home = Team(data["home"])
        self.away = Team(data["away"])

    def get_stats(self):
        url = Urls.statistics(self.id)
        data = requests.get(url).json()
        data = data["statistics"]
        data = {
            p.pop("period"): p for p in data
        }

        data = {
            p: data[p]["groups"] for p in data
        }

        for p in data:
            for stats in data[p]:
                for i,stat in enumerate(stats["statisticsItems"]):
                    stats["statisticsItems"][i] = {
                        "name": stat["name"],
                        "homeValue": stat["homeValue"],
                        "awayValue": stat["awayValue"]
                    }
    
        return data
