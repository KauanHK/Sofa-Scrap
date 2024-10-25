"""Executa o programa"""

def main():

    from database import MainTournaments, Categories
    from stats import Statistics
    main_tournaments = MainTournaments()
    tournament = main_tournaments.input()
    if tournament == 'outro':
        print('outro otnrio')
        cats = Categories()
        cat = cats.input()
        tournament = cat.input()
        
    season = tournament.input()

    stats = Statistics(season)
    n = stats.input()
    stats.save(n)

if __name__ == '__main__':
    main()