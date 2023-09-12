import requests
from datetime import datetime
from pars_1x_stg import send_telegram

def get_message(corners):
    league, team_1, team_2, timestamp, total, total_hight, total_low = corners.values()
    timestamp = corners['S']
    game_date = datetime.fromtimestamp(timestamp).strftime('%d.%m %H:%M')
    message = f'{league} ({game_date})\n' \
                f'{team_1} - {team_2}\n' \
                f'\n' \
                f'ТМ {total} # {total_low}\n' \
                f'ТБ {total} # {total_hight}'
    send_telegram(message)
    print(message)

# Вместо этого используем БД(любую)
def search_db(game_id, corners):
    
    with open('db.txt', 'r') as file:
        lines = file.readlines()
        print(lines)
        if str(game_id) + '\n' not in lines: 
            get_message(corners)
    
    with open('db.txt', 'a') as file:
        file.write(f'{game_id}\n')         

def get_corners(game_result, game_id):

    for game in game_result['Value']:
        current_id = game['I']
        if current_id == game_id:
            corners = {}
            corners['L'] = game['L']
            corners['O1'] = game['O1']
            corners['O2'] = game['O2']
            corners['S'] = game['S']
            bets = game['SG']
            for item in bets:
                try:
                    bet = item['TG']
                except:    
                    bet = item['PN']
                if 'Угловые' in bet:
                    for node in item['E']:
                        table_c = node['T']
                        
                        if 9 == table_c:
                            total = node['P']
                            coef = node['C']
                            corners['total'] = total
                            corners['total_hight'] = coef
                        
                        if 10 == table_c:
                            coef = node['C']
                            corners['total_low'] = coef
                    search_db(game_id, corners)
            print('===================================================')


def get_game(result):
    
    for game in result['Value']:
        game_id = game['I']
        champs = game['LI']

        params = {
        'sports': '1',
        'champs': champs,
        'count': '50',
        'tf': '2200000',
        'tz': '3',
        'antisports': '188',
        'mode': '4',
        'subGames': game_id,
        'country': '1',
        'partner': '51',
        'getEmpty': 'true',
        }
        response = requests.get('https://1xstavka.ru/LineFeed/Get1x2_VZip', params=params)
        game_result = response.json()
        get_corners(game_result, game_id)
        break

def main():
    url = 'https://1xstavka.ru/line/football/1793471-norway-eliteserien/'
    champs = url.split('/')[-2].split('-')[0]
    
    params = {
    'sports': '1',
    'champs': champs,
    'count': '50',
    'tf': '2200000',
    'tz': '3',
    'antisports': '188',
    'mode': '4',
    'country': '1',
    'partner': '51',
    'getEmpty': 'true',
    }

    response = requests.get('https://1xstavka.ru/LineFeed/Get1x2_VZip', params=params)
    result = response.json()
    get_game(result)
    
if __name__ == '__main__':
    main()