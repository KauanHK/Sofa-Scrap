"""Executa o programa"""

def main():

    from database import MainTournaments
    main_tournaments = MainTournaments()
    tournament = main_tournaments.input()
    if tournament == 'outro':

        from database import Categories
        cats = Categories()
        cat = cats.input()
        tournament = cat.input()
        
    season = tournament.input()
    season.load()

if __name__ == '__main__':
    main()