import requests
import json
import csv
import os
from typing import Literal, Any



class Urls:
    """Urls da api do SofaScore"""

    @staticmethod
    def categories():
        return "https://www.sofascore.com/api/v1/sport/football/categories"
    
    @staticmethod
    def category(id): 
        return f"https://www.sofascore.com/api/v1/category/{id}/unique-tournaments"
    
    @staticmethod
    def tournament(id):
        return f"https://api.sofascore.com/api/v1/unique-tournament/{id}/seasons"
    
    @staticmethod
    def season(tournament_id, season_id, round):
        return f"https://www.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{season_id}/events/round/{round}"
    
    @staticmethod
    def statistics(event_id):
        return f"https://www.sofascore.com/api/v1/event/{event_id}/statistics"
    
    @staticmethod
    def event(id):
        return f"https://www.sofascore.com/api/v1/event/{id}"
    
    @staticmethod
    def main_tournaments(): 
        return "https://www.sofascore.com/api/v1/config/top-unique-tournaments/BR/football"
    


File = Literal["categories", "category", "tournament", "season", "statistics"]

def get_file_path(file: File, *args: str, makedirs: bool = False):
    """Retorna o caminho do arquivo"""

    with open("filenames.json", 'r') as f:
        file_path = json.load(f)[file]
    if args:
        file_path = file_path.format(*args)
    if makedirs:
        os.makedirs(os.path.split(file_path)[0], exist_ok=True)
    return file_path


def load_json(file: File, *args) -> dict:
    """Carrega um json. Se o arquivo não existir, retorna None"""

    file_path = get_file_path(file, *args)
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r') as f:
        return json.load(f)

def load_csv(file: File, *args):
    file_path = get_file_path(file, *args)
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r') as f:
        return list(csv.reader(f))[1:]

def save_json(data, file: File, *args, update: bool = True, makedirs: bool = True):

    file_path = get_file_path(file, *args, makedirs=makedirs)
    if update and os.path.exists(file_path):
        data.update(load_json(file, *args))

    with open(file_path, 'w') as f:
        try:
            json.dump(data, f, indent=4, ensure_ascii=False)
        except UnicodeEncodeError:
            json.dump(data, f, indent=4)


def save_csv(data, file: File, *args, update: bool = True, makedirs: bool = True):

    file_path = get_file_path(file, *args, makedirs)
    if update:
        current_data = load_csv(file, *args)
        if current_data is not None:
            data.extend(current_data)

    with open(file_path, 'w') as f:
        csv.writer(f).writerows(data)



class Base:

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
    
    def json(self):
        if self.is_saved():
            return load_json(*self.locator)
        data = self._load()
        save_json(data, *self.locator)
        return data
    
    def is_saved(self) -> bool:
        file_path = get_file_path(*self.locator)
        return os.path.exists(file_path)