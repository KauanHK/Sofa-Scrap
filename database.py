import requests
import os
from utils import Urls, File, get_file_path, load_json, Base


def has_saved(file: File, *args: str) -> bool:
    file_path = get_file_path(file, *args)
    return os.path.exists(file_path)

class Categories(Base):

    def __init__(self):
        self.url = Urls.categories()
        self.file = "categories"
        self.data = self.json()

    def _load(self):
        data = requests.get(self.url).json()
        data = data["categories"]
        data = {c["name"]: c["id"] for c in data}
        return data

    def json(self):
        if has_saved(self.file):
            return load_json(self.file)
        return self._load()
    
    def get_category(self, id: int | None = None, name: str | None = None):
        
        if id is not None:
            return Category(id, self.get_name(id))
        return Category(self.get_id(name), name)
            
    
class Category(Base):
    
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.file = "tournament"
        self.data = self.json()

    def json(self):
        if has_saved(self.file, self.name):
            return load_json(self.file, self.name)
        return self._load()

    def _load(self):
        url = Urls.tournament(self.id)
        data = requests.get(url).json()
        data = data["seasons"]
        filter_data = {}
        for season in data:
            del season["editor"]
            name = season["name"]
            filter_data[name] = season
        return filter_data
    
    def get_tournament(self, id: int | None = None, name: str | None = None):
        if id is not None:
            return Tournament(id, self.get_name(id))
        return Tournament(self.get_id(name), name)
        

class Tournament:

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name