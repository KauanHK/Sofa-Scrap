import requests
from utils import Urls, FileNames, save_json, load_json
import os
from typing import Union, Literal, overload



class Base:

    def __init__(self, id: int, name: str, file_path: str | None = None):
        self.id = id
        self.name = name
        self.file_path = file_path
        self.data: dict[str, dict]

    def get_name(self, id: int) -> str:
        for c in self.data:
            if self.data[c] == id:
                return c
        raise ValueError(f'id {id} não encontrado')
            
    def get_id(self, name: str) -> int:
        for c in self.data:
            if c == name:
                return self.data[c]
        raise ValueError(f'Nome {name} não encontrado')
    
    def load(self):
        
        data_object = self.__class__.__name__
        print(f"Carregando {data_object}")
        
        current_data = None
        if self.is_saved():
            current_data = load_json(self.file_path)

        if current_data is None:
            data = self._load()
        elif data_object == "Season":
            matches_per_round = 0
            for k in current_data:
                if len(current_data[k]) > matches_per_round:
                    matches_per_round = len(current_data[k])

            rounds = []
            for k in current_data:
                if len(current_data[k]) < matches_per_round:
                    n = int(k[6:])
                    rounds.append(n)

            if not len(rounds):
                rounds = range(len(current_data), 1000)
            data = self._load(rounds)

        if current_data is not None:
            data.update(current_data)
        
        if hasattr(self, 'file_path') and self.file_path is not None:
            print('Salvando', os.path.split(self.file_path)[1])
            save_json(data, self.file_path)

        return data
    
    def is_saved(self) -> bool:
        if hasattr(self, 'file_path') and self.file_path is not None:
            return os.path.exists(self.file_path)
    
    def get_all_names(self) -> list[str]:
        return list(self.data)

    def _load(self):
        raise NotImplementedError(f'{self.__class__.__name__} não possui o método _load()')
    
    @overload
    def _input(data: dict, data_object: "Category", *args, order: bool = False) -> "Category": ...
    @overload
    def _input(data: dict, data_object: "Tournament", *args, order: bool = False) -> "Tournament": ...
    @overload
    def _input(data: dict, data_object: "Season", *args, order: bool = False) -> "Season": ...

    def _input(self, data: dict, data_object: Union["Category", "Tournament", "Season"], *args, order: bool = False) -> Union["Category", "Tournament", "Season"]:

        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

        if order:
            print_data = sorted(data)
        else:
            print_data = list(data)
        
        while True:

            for i,d in enumerate(print_data, 1):
                print(f'{i} - {d}')
        
            try:
                i = int(input("Escolha opção: "))
                name = print_data[i-1]
                id = data[name]["id"] if isinstance(data[name], dict) else data[name]
                return data_object(id, name, *args)
            except ValueError:
                print('Entrada inválida')


class MainTournaments(Base):

    def __init__(self):

        self.url = Urls.main_tournaments()
        self.data = self.load()

    def _load(self) -> dict[str, dict]:
        data = requests.get(self.url).json()
        data = data["uniqueTournaments"]

        result = {}
        for t in data:
            result[t["name"]] = {
                "id": t["id"],
                "name": t["name"],
                "category": {
                    "id": t["category"]["id"],
                    "name": t["category"]["name"]
                }
            }
        return result

    def input(self) -> Union["Tournament", Literal["outro"]]:
        
        outro = len(self.data) + 1
        tournaments = list(self.data)
        while True:
            for i,t in enumerate(tournaments, 1):
                print(f'{i} - {t}')
            print(f'{outro} - Outro')
            try:
                i = int(input("Escolha uma opção: ")) - 1
                
                if i == outro:
                    return 'outro'
                elif i < 0 or i > outro:
                    print('Entrada inválida')
                else:
                    tournament_name = tournaments[i]
                    category = Category(
                        id = self.data[tournament_name]["category"]["id"],
                        name = self.data[tournament_name]["category"]["name"]
                    )
                    id = self.data[tournament_name]["id"]
                    return Tournament(id, tournament_name, category)
            except ValueError:
                break

        


class Categories(Base):

    def __init__(self):

        self.url = Urls.categories()
        self.locator = ("categories",)
        self.data = self.load()
        
    def input(self) -> "Category":
        return self._input(self.data, Category, order=False)

    def load(self):
        
        data = requests.get(self.url).json()
        data = data["categories"]
        data = {c["name"]: c["id"] for c in data}
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
        self.data = self.load()
        
    def input(self) -> "Tournament":
        return self._input(self.data, Tournament, self)

    def load(self):
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
        

class Tournament(Base):

    def __init__(self, id: int, name: str, category: Category):

        super().__init__(id, name)
        self.category = category
        self.data = self.load()
        
    def input(self) -> "Season":
        return self._input(self.data, Season, self.category, self)

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

    def input(self) -> None:
        pass

    def _get_file_name(self, category: Category, name: str) -> str:
        return FileNames.season(category.name, name)

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
                "status": status,
                "id": match["id"]
            }

        return filter_data
    
    def get_rounds(self, save: bool = True) -> list[list["Match"]]:
        self._save = save
        data = self.load()
        return self._create_match_objects(data)

    def _create_match_objects(self, data: dict[str, dict[str, dict]]) -> list[list["Match"]]:
        matches: list[Match] = []
        for round in data:
            round_data = []
            for match in data[round]:
                match_data = Match(data[round][match], self.category)
                round_data.append(match_data)
            matches.append(round_data)
        return matches

    def _load(self, rounds: list[int] | None = None):

        data: dict[str, dict] = {}
        if rounds is None:
            rounds = range(1, 1000)
        for n in rounds:
            round = self.load_round(n)
            if round is None:
                break
            data[f'rodada{n}'] = round
            
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