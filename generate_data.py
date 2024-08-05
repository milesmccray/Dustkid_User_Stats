"""
Generate JSON following this format:

[
{column1:value1, column2:value2,...},
{column1:value2, column2:value2,...},
]

Generate a json file with all top players username, best rank, worst rank, average rank (ss, any, all)
# of achievements, basically anything on dustkid but generate it into a file (csv?) that can be
put into google sheets
"""
import json
import requests
import pandas as pd


def main():
    # Load Top 300 DF Overall Players ID Numbers / Usernames
    with open('dk_users.json', 'r') as f:
        data = json.load(f)

    json_data = []
    count = 0
    for usr_id, usr_name in data['Users'].items():
        count += 1
        print(f'Requesting dustkid data for user {count}, ID #:` {usr_id}...')
        levels_json = requests.get(f'https://dustkid.com/json/profile/{usr_id}/').json()

        ss_ranks, any_ranks = grab_level_info(levels_json)

        (usr_ss_10, usr_ss_wr, usr_any_10, usr_any_wr, usr_total_10, usr_total_wr, usr_best_ss, usr_worst_ss,
         usr_best_any, usr_worst_any, usr_avg_ss, usr_avg_any, usr_avg_all) = calculate_data(ss_ranks, any_ranks)

        json_data = create_json(json_data, usr_name, usr_id, usr_ss_10,
                                usr_ss_wr, usr_any_10, usr_any_wr, usr_total_10,
                                usr_total_wr, usr_best_ss, usr_worst_ss,
                                usr_best_any, usr_worst_any, usr_avg_ss,
                                usr_avg_any, usr_avg_all)

    # Dump Data to JSON
    with open('dustkid_user_data.json', 'w') as f:
        json.dump(json_data, f, indent=3)

    # Create Excel Document of top 500 users
    df = pd.read_json('dustkid_user_data.json')
    df.to_excel('output.xlsx')


def grab_level_info(json_data: dict) -> dict:
    """Grabs rank information on every level"""
    # Skip list
    other_levels = ['The-Dustforce-DX-5583', 'The-Scrubforce-DX-6018', 'The-Difficults-5462', 'The-Lab-4563',
                    'The-City-2800', 'The-Mansion-5517', 'The-Forest-2654', 'exec func ruin user', 'tutorial0']
    # SS
    ss_ranks = {}
    for level in json_data['ranks_scores']:
        if level not in other_levels:
            # Uses the point scoring to determine rank due to ties on leaderboard. 0 points = 1st
            ss_ranks[level] = json_data['ranks_scores'][level]['points'] + 1

    # Any
    any_ranks = {}
    for level in json_data['ranks_times']:
        if level not in other_levels:
            # Uses the point scoring to determine rank due to ties on leaderboard. 0 points = 1st
            any_ranks[level] = json_data['ranks_times'][level]['points'] + 1

    return ss_ranks, any_ranks


def grab_extra_info(html):
    """Parses user's html page for name and extra stats
    NOTE: NOT NEEDED UNTIL ACHIEVEMENTS + OTHER STATS ARE AVAILABLE"""
    extra_info = html.find('ul').find_all('li')


def calculate_data(ss_data: dict, any_data: dict):
    # Count top 10's and WR's
    usr_ss_10 = 0
    usr_ss_wr = 0
    usr_any_10 = 0
    usr_any_wr = 0
    usr_total_10 = 0
    usr_total_wr = 0
    for rank in ss_data.values():
        if rank <= 10:
            usr_ss_10 += 1
        if rank == 1:
            usr_ss_wr += 1
    for rank in any_data.values():
        if rank <= 10:
            usr_any_10 += 1
        if rank == 1:
            usr_any_wr += 1

    usr_total_10 = usr_ss_10 + usr_any_10
    usr_total_wr = usr_ss_wr + usr_any_wr

    # Get Best and Worst Ranks (Returns a tuple with levelname and rank)
    usr_best_ss = min(ss_data.values())
    usr_worst_ss = max(ss_data.values())
    usr_worst_any = max(any_data.values())

    # Calculate Best Any W/O Construction Site Frame
    temp_any_data = any_data.copy()
    while True:
        try:
            del temp_any_data["boxes"]
            break
        except KeyError:
            break

    usr_best_any = min(temp_any_data.values())

    # Calculate Averages
    ss_num = len(ss_data)
    ss_total = 0
    for x in ss_data.values():
        ss_total += x
    usr_avg_ss = round((ss_total / ss_num), 2)

    any_num = len(any_data)
    any_total = 0
    for x in any_data.values():
        any_total += x
    usr_avg_any = round((any_total / any_num), 2)

    all_num = ss_num + any_num
    all_total = ss_total + any_total
    usr_avg_all = round((all_total / all_num), 2)

    return (usr_ss_10, usr_ss_wr, usr_any_10, usr_any_wr, usr_total_10, usr_total_wr, usr_best_ss, usr_worst_ss,
            usr_best_any, usr_worst_any, usr_avg_ss, usr_avg_any, usr_avg_all)


def create_json(json_data: list, usr_name: str, usr_id: int, usr_ss_10: int, usr_ss_wr: int, usr_any_10: int,
                usr_any_wr: int, usr_total_10: int, usr_total_wr: int, usr_best_ss: int, usr_worst_ss: int,
                usr_best_any: int, usr_worst_any: int, usr_avg_ss: int, usr_avg_any: int,
                usr_avg_all: int):
    json_data.append({'username': usr_name, 'dustkid_id': usr_id, 'ss_top_10s': usr_ss_10, 'ss_wrs': usr_ss_wr,
                      'any%_top_10s': usr_any_10, 'any%_wrs': usr_any_wr, 'total_top_10s': usr_total_10,
                      'total_wrs': usr_total_wr, 'best_ss_rank': usr_best_ss, 'worst_ss_rank': usr_worst_ss,
                      'best_any%_rank': usr_best_any, 'worst_any%_rank': usr_worst_any, 'avg_ss_rank': usr_avg_ss,
                      'avg_any%_rank': usr_avg_any, 'avg_overall_rank': usr_avg_all})
    return json_data


main()
