from sofa_scrap.utils import Urls, get_data, save_json


class Tournament:

    def __init__(self, id: int, category):
        self.id = id

    def save(self):
        url = Urls.TOURNAMENT
        save_json(get_data(url), "tournament", self)