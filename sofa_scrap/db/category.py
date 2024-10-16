from sofa_scrap.utils import Urls
from sofa_scrap.utils import save_json, get_data, get_name, load_json
from sofa_scrap.db.tournament import Tournament


class Category:

    def __init__(self, id):
        self.id = id

    def save(self):
        
        url = Urls.CATEGORY.format(self.id)
        
        data = get_data(url)
        data = data["groups"][0]["uniqueTournaments"]
        data = {t["name"]: t["id"] for t in data}

        categoria = get_name(load_json("categories"), self.id)
        save_json(data, "category", categoria)
        print(f"Categoria {categoria} salva com sucesso")

    def get_tournament(self, id: int) -> Tournament:
        return Tournament(id, self)