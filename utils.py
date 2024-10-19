import requests
import json
import csv
import os
from typing import Literal, Any



class Urls:
    """Urls da api do SofaScore"""

    CATEGORIES = "https://www.sofascore.com/api/v1/sport/football/categories"
    CATEGORY = "https://www.sofascore.com/api/v1/category/{}/unique-tournaments"
    # MAIN_TOURNAMENTS = "https://www.sofascore.com/api/v1/config/top-unique-tournaments/BR/football"
    TOURNAMENT = "https://api.sofascore.com/api/v1/unique-tournament/{}/seasons"
    SEASON = "https://www.sofascore.com/api/v1/unique-tournament/{}/season/{}/events/round/{}"
    STATISTICS = "https://www.sofascore.com/api/v1/event/{}/statistics"
    EVENT = "https://www.sofascore.com/api/v1/event/{}"


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


def get_data(url):
    return requests.get(url).json()

def get_name(data, id: int):

    if data is None:
        raise FileNotFoundError('É necessário carregar os dados primeiro.')

    for c in data:
        if data[c] == id:
            return c
    raise ValueError(f'Erro: id={id} não encontrado.')