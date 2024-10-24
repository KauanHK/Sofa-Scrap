import requests
from database import Season
from utils import Urls, save_json


class Statistics:

    def __init__(self, season: Season):
        self.season = season

    def input(self) -> int:
        
        while True:

            try:
                return int(input('Pegar estatísticas de quantas rodadas? '))
            except ValueError:
                print('Entrada inválida')
            except KeyboardInterrupt:
                print("Programa finalizado")
            except Exception as e:
                print(repr(e))

    
    def json(self):

        response_data = requests.get(self.url).json()
        response_data = response_data["statistics"]
        
        data = {}
        for dict_ in response_data:
            period = dict_["period"]
            groups = dict_["groups"]
            data[period] = {group.pop("groupName"): group["statisticsItems"] for group in groups}
            for group in data[period]:
                stats = {}
                for stat in data[period][group]:
                    stats[stat["name"]] = {
                        "home": stat["homeValue"],
                        "away": stat["awayValue"]
                    }
                data[period][group] = stats

        return data


    def load_round(self, round: int):

        url = Urls.season(self.season.tournament.id, self.season.id, round)
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

    def load_match(self) -> dict:
        
        data = {}
        round = current_round
        while len(data) < n:
            data_round = self.load_round(round)
            if data_round is not None:
                print(f'Rodada {round}', end='   \r')
                data[round] = data_round
            round -= 1
        return data
            

    def save(self, n: int):

        url = Urls.rounds(self.season.tournament.id, self.season.id)
        current_round = requests.get(url).json()
        current_round = len(current_round["rounds"])

        for 
        data = self.load(n)
        filename = f'{self.home} x {self.away}.json'
        filename = './a.json'
        save_json(data, filename)


if __name__ == '__main__':
    Statistics