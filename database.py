import requests
from utils import Urls, FileNames, save_json, get_file_path
import os
from typing import Union, Literal



class Base:

    def __init__(self, id: int, name: str, file_path: str | None = None):
        self.id = id
        self.name = name
        self.file_path = file_path
        self.data: dict | None = None
        self._save = self.file_path is not None

    def get_name(self, id: int) -> str:

        if self.data is None:
            self.data = self.load()
            
        for c in self.data:
            if self.data[c] == id:
                return c
        raise ValueError(f'id {id} não encontrado')
            
    def get_id(self, name: str) -> int:
        if name not in self.data:
            raise ValueError(f'Nome {name} não encontrado')
        return self.data[name]
    
    def save(self) -> None:

        if self.data is None:
            self.data = self.load()

        file_path = get_file_path(self.__class__.__name__)
        save_json(self.data, file_path)

    def load(self):
        raise NotImplementedError(f'Método load não foi implementado a {self.__class__.__name__}')

    def is_saved(self) -> bool:
        if self._save:
            return os.path.exists(self.file_path)
    
    def get_all_names(self) -> list[str]:
        return list(self.data)
    
    def input(self) -> Union["Category", "Tournament", "Season"]:

        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

        data = self.load()
        options = list(data)
        
        while True:

            self._display_options(options)
        
            try:
                option = input("Escolha opção: ")
                i = int(option) - 1
                name = options[i]
                id = data[name]["id"] if isinstance(data[name], dict) else data[name]
                return self.__class__(id, name)
            except ValueError:
                print('Entrada inválida')

    def _display_options(self, options: list[str]) -> None:
        for i,d in enumerate(options, 1):
            print(f'{i} - {d}')

class MainTournaments(Base):

    def __init__(self):
        self.url = Urls.main_tournaments()

    def load(self) -> dict[str, dict]:

        response_data = requests.get(self.url).json()
        response_data = response_data["uniqueTournaments"]

        data = {}
        for t in response_data:
            data[t["name"]] = {
                "id": t["id"],
                "name": t["name"],
                "category": {
                    "id": t["category"]["id"],
                    "name": t["category"]["name"]
                }
            }
        return data

    def input(self) -> Union["Tournament", Literal["outro"]]:
        
        data = self.load()
        outro = len(data) + 1
        tournaments = list(self.data)
        while True:
            for i,t in enumerate(tournaments, 1):
                print(f'{i} - {t}')
            print(f'{outro} - Outro')
            try:
                i = int(input("Escolha uma opção: "))
                
                if i == outro:
                    return 'outro'
                elif i < 1 or i > outro:
                    print('Entrada inválida')
                else:
                    tournament_name = tournaments[i-1]
                    category = Category(
                        id = self.data[tournament_name]["category"]["id"],
                        name = self.data[tournament_name]["category"]["name"]
                    )
                    id = self.data[tournament_name]["id"]
                    return Tournament(id, tournament_name, category)
            except ValueError:
                break

    def _display_tournaments(self): ...


class Categories(Base):

    def __init__(self):

        self.url = Urls.categories()
        self.locator = ("categories",)
        
    def load(self) -> dict[str, int]:
        data = requests.get(self.url).json()
        data = data["categories"]
        data = {c["name"]: c["id"] for c in data}
        return data

    def get_category(self, id: int | None = None, name: str | None = None):
        if id is not None:
            return Category(id, self.get_name(id))
        return Category(self.get_id(name), name)
    
    def get_categories(self) -> list["Category"]:
        categories: list[Category] = []
        for name, id in self.load().items():
            cat = Category(id, name)
            categories.append(cat)
        return categories
    
class Category(Base):
    
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        
    def input(self) -> "Tournament":
        return self._input(self.data, Tournament, self)

    def load(self) -> dict[str, int]:
        url = Urls.category(self.id)
        data = requests.get(url).json()
        data = data["groups"][0]["uniqueTournaments"]
        data = {t["name"]: t["id"] for t in data}
        return data
    
    def get_tournament(self, id: int | None = None, name: str | None = None):
        if id is not None:
            return Tournament(id, self.get_name(id), self)
        elif name is not None:
            return Tournament(self.get_id(name), name, self)
        name = self.get_all_names()[0]
        return Tournament(self.data[name], name, self)
        
    def get_tournaments(self) -> list["Tournament"]:
        tournaments: list[Tournament] = []
        for name, id in self.load().items():
            t = Tournament(id, name, self)
            tournaments.append(t)
        return tournaments

class Tournament(Base):

    def __init__(self, id: int, name: str, category: Category):

        super().__init__(id, name)
        self.category = category
        
    def load(self) -> dict[str, dict]:
        url = Urls.tournament(self.id)
        response_data = requests.get(url).json()
        response_data = response_data["seasons"]
        data = {}
        for s in response_data:
            data[s["name"]] = {
                "year": s["year"],
                "id": s["id"]
            }
        return data
    
    def get_name(self, id: int) -> str:
        for c in self.data:
            if self.data[c]["id"] == id:
                return c
        raise ValueError(f'id {id} não encontrado')
    
    def get_id(self, name: str) -> int:
        if name not in self.load():
            raise ValueError(f"Nome {name} não encontrado")
        return self.data[name]["id"]

    def get_seasons(self, n: int = 1) -> list["Season"]:
        seasons: list[Season] = []
        for i,s in enumerate(self.data,1):
            id = self.data[s]["id"]
            season = Season(id, s, self.category, self)
            seasons.append(season)
            print(i)
            if i >= n:
                break
        return seasons
        

class Season(Base):

    def __init__(self, id: int, name: str, category: Category, tournament: Tournament):
        file_name = self._get_file_name(category, name)
        super().__init__(id, name, file_name)
        self.category = category
        self.tournament = tournament

    def _get_file_name(self, category: Category, name: str) -> str:
        return FileNames.season(category.name, name)
    
    def get_rounds(self, save: bool = True) -> list[list["Match"]]:
        self._save = save
        data = self.load()
        return self._create_match_objects(data)

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
                if not len(filter_data):
                    return None
                continue
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
                "id": match["id"]
            }

        return filter_data

    def _create_match_objects(self, data: dict[str, dict[str, dict]]) -> list[list["Match"]]:
        matches: list[Match] = []
        for round in data:
            round_data = []
            for match in data[round]:
                match_data = Match(data[round][match], self.category)
                round_data.append(match_data)
            matches.append(round_data)
        return matches

    def load(self, rounds: list[int] | None = None) -> dict[int, dict]:

        data: dict[str, dict] = {}
        if rounds is None:
            rounds = range(1, 1000)
        for n in rounds:
            round = self.load_round(n)
            if round is None:
                break
            data[n] = round
            
            print(f'Rodada {n}   ', end='\r')
        print()

        return data
    

class Match(Base):

    def __init__(self, data: dict[str, dict], category: Category):
        self.home = Team(data["home"])
        self.away = Team(data["away"])
        self.category = category

        name = f'{self.home.name} x {self.away.name}'
        file_path = self._get_file_path(name)
        super().__init__(data["id"], name, file_path)

    def _get_file_path(self, file_name: str):
        return FileNames.statistics(self.category.name, file_name)

    def _load(self):

        url = Urls.statistics(self.id)
        data = requests.get(url).json()

        data = data["statistics"]
        data = {
            p.pop("period"): p for p in data
        }

        data = {
            p: data[p]["groups"] for p in data
        }

        for i,p in enumerate(data):
            for stats in data[p]:
                for i,stat in enumerate(stats["statisticsItems"]):
                    stats["statisticsItems"][i] = {
                        "name": stat["name"],
                        "homeValue": stat["homeValue"],
                        "awayValue": stat["awayValue"]
                    }
    
        return data


class Team(Base):
     
    def __init__(self, data: dict[str, str | int]):
        super().__init__(data["id"], data["name"])
        self.period1 = data["period1"]
        self.period2 = data["period2"]
        self.score = data["normaltime"]
