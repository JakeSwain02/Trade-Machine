import pprint as p
import xlrd
import numpy as np
import statistics as s
import matplotlib.pyplot as plt
from astropy.table import Table
import numpy as np
from operator import itemgetter

def get_data(file, sheet):
    book = xlrd.open_workbook(file)
    sheet = book.sheet_by_name(sheet)
    data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
    return data

def int_data(file):
    player_stats = get_data(file, 'p_19')
    team_stats = get_data(file, 's_19')
    sal_stats = get_data(file, 'sals')
    pos_stats = get_data(file, 'poses')

    rank, TEAM, GP, W, L, WIN_p, MIN, PTS, FGM, FGA, FG_p, three_p, FTM, FTA, FT_p, OREB, DREB,  REB,  AST,	 TOV,  STL,  BLK,  PF,  BLKA,  PF,  PFD,  plus_min = [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],  [], [], [], [], []
    league_stats = [ rank,  TEAM,  GP,  W,  L,  WIN_p,  MIN,  PTS,  FGM,  FGA,  FG_p,  three_p,  FTM,  FTA,  FT_p,  OREB,  DREB,  REB,  AST,  TOV,  STL,  BLK,  PF,  BLKA,  PF,  PFD,  plus_min]

    for player in range(len(player_stats)):
        for i in range(4):
            del player_stats[player][-1]
        del player_stats[player][5]
        del player_stats[player][5]
        del player_stats[player][3]
        del player_stats[player][0]

    for team in range(len(team_stats)):
        del team_stats[team][-1]
        del team_stats[team][-1]
        del team_stats[team][-2]
        for i in range(3):
            del team_stats[team][3]

    for stat in range(len(team_stats[0]) - 1):
        for team in range(len(team_stats) - 1):
            league_stats[stat].append(team_stats[team + 1][stat])

    team_stats[0][0] = 'Winning'

    return player_stats, league_stats, team_stats, sal_stats, pos_stats

def project_stats(league_stats, year):

    league_stats_avg, league_stats_sd, league_stats_projected_avg = [], [], []

    for stat in league_stats:
        try:
            league_stats_avg.append(s.mean(stat))
        except:
            league_stats_avg.append(0)

    for stat in league_stats:
        try:
            league_stats_sd.append(s.stdev(stat))
        except:
            league_stats_sd.append(0)


    # run regressions/
    league_stats_projected_avg = league_stats_avg


    return league_stats_projected_avg, league_stats_sd

def find_team_row(team_stats, team_name):

    for team in range(len(team_stats)):
        if team_stats[team][1] == team_name:

            team_row = team
    return team_row

def show_player_stats(player_stats, player_name):

    for player in range(len(player_stats)):
        if player_name == player_stats[player][0]:


            return player_stats[player]

def find_best_fit(league_stats_sd, league_stats_projected_avg, team_name, team_stats, player_stats, pos_stats, player_type):

    fit_ratings = []
    stats_used = ['PLAYER', 'TEAM', 'FGM', 'FGA', 'FTM','3PM', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'FOUL']
    weights = [ 0.045170/0.37975 , .001138/0.379759, 0.062897/0.379759, 0.051906/0.379759, 0.009412/0.379759, 0.066046/0.379759, -0.069544/0.379759, 0.008639/0.379759, 0.006232/0.379759]
    team_row = find_team_row(team_stats, team_name)


    for player in range(len(player_stats)):

        summ_player_team = 0
        summ_team = 0
        fit_ratings.append([])
        for stat in range(len(player_stats[0]) - 1):
            try:
                for stat_used in range(len(stats_used)):
                    if player_stats[0][stat] == stats_used[stat_used]:

                        ratio_per_point = league_stats_projected_avg[stat] / league_stats_projected_avg[6]
                        # print(round(ratio_per_point,3), player_stats[0][stat]  )
                        ratio_scale = team_stats[team_row][6] + player_stats[player][6]
                        adjusted_adv_stat = ratio_per_point * ratio_scale
                        combinded_stat = (team_stats[team_row][stat] + player_stats[player][stat])
                        combinded_stat_z = (combinded_stat - adjusted_adv_stat) / league_stats_sd[stat]
                        team_z = (team_stats[team_row][stat] - adjusted_adv_stat) / league_stats_sd[stat]

                        if combinded_stat_z < 0:
                            summ_player_team = summ_player_team + abs(combinded_stat_z)
                            summ_team = summ_player_team + abs(combinded_stat_z)

                        fit_ratings[player].append(combinded_stat_z)
            except:
                fit_ratings[player].append(player_stats[player][stat])
            fit_ratings[player].append(summ_player_team)

    fit_ratings = sorted(fit_ratings, key=itemgetter(-1))

    return fit_ratings

def find_w_s(team_stats, league_stats_projected_avg, team_name, league_stats_sd):

    team_row = find_team_row(team_stats,team_name)
    arr, team_stat_ratings = [], []

    for stat in range(len(team_stats[team_row])):
        try:
            if league_stats_sd[stat] == 0:
                team_stat_ratings.append(0)
            else:
                stat_rating = (team_stats[team_row][stat] - league_stats_projected_avg[stat]) / (league_stats_sd[stat])
                team_stat_ratings.append(stat_rating)
        except:
            team_stat_ratings.append(0)
    team_stat_ratings[0] = (0 - team_stat_ratings[0])
    team_stat_ratings[15] = (0 - team_stat_ratings[15])


    stats_shown = [ 'FGM', 'FTM','3PM', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'FOUL']

    for stat in range(len(team_stat_ratings)):
        for stat_shown in stats_shown:
            # print(team_stats[0][stat], stat_shown)

            if team_stats[0][stat] == stat_shown:
                # print(stat)
                arr.append([team_stats[0][stat], round(team_stat_ratings[stat],3)])

    arr = sorted(arr, key=itemgetter(-1))



    team_weakness = [arr[0], arr[1], arr[2], arr[3], arr[4]]

    return team_weakness

def find_trade(fit_ratings, team_stats, player_stats, league_stats_sd, league_stats_projected_avg, team_name, sal_stats, max_cap_hit, pos_stats, player_type):

    trade_away, possible_trades= [], []
    # for player in range(len(fit_ratings)):
    for player in range(50):
        target_team = fit_ratings[player][2]

        t_partner_fit_ratings = find_best_fit(league_stats_sd, league_stats_projected_avg, target_team, team_stats, player_stats, pos_stats, player_type)
        for player_2 in range(50):
            if t_partner_fit_ratings[player_2][2] == team_name:
                trade_away.append([t_partner_fit_ratings[player_2][0], fit_ratings[player][0], (player_2 +player)])
                break

    trade_away = sorted(trade_away, key=itemgetter(-1))

    for trade in range(len(trade_away)):
        player1_sal, player2_sal = 0, 0

        for sal in range(len(sal_stats)):
            if trade_away[trade][0] == sal_stats[sal][1]:
                player1_sal = sal_stats[sal][3]
            if trade_away[trade][1] == sal_stats[sal][1]:
                player2_sal = sal_stats[sal][3]

        trade_away[trade].append(round(player1_sal,3))
        trade_away[trade].append(round(player2_sal,3))
        trade_away[trade].append(round(player1_sal - player2_sal,3))

    for trade in range(len(trade_away)):
        if trade_away[trade][-1] < abs(max_cap_hit):
            possible_trades.append(trade_away[trade])

    return possible_trades

def display(team_weakness, fit_ratings, team_stats, player_stats, team_name, file, trades, league_stats_projected_avg, league_stats_sd):

    team_row = find_team_row(team_stats, team_name)
    suggested = []
    suggested_rows = []

    player_stats_raw = get_data(file, 'p_19')

    for player in range(5):
        suggested.append(fit_ratings[player + 1][0])

    for player_sug in range(len(suggested)):
        for player_all in range(len(player_stats)):
            if suggested[player_sug] == player_stats[player_all][0]:
                suggested_rows.append(player_all)

    for i in range(len(fit_ratings)):
        for j in range(len(fit_ratings[i])):
            try:
                fit_ratings[i][j] = round(fit_ratings[i][j], 2)
                if fit_ratings[i][j] > 10:
                    fit_ratings[i][j] == 0
            except:
                continue

    print('...')
    print(team_name, 'Weakest Areas: ', team_weakness)
    print('...')
    print('Suggested Players:')
    for row in range(len(suggested_rows)):
        print(row + 1)
        if player_stats[suggested_rows[row]][2] > 10:
            for stat in range(len(player_stats[0])):
                print(player_stats[0][stat], player_stats[suggested_rows[row]][stat])
            try:
                print('On', team_name, trades[row][0], 'Best Fits', player_stats[suggested_rows[row]][1])
                print(player_stats[suggested_rows[row]][1], 'Team Needs: ',find_w_s(team_stats, league_stats_projected_avg, player_stats[suggested_rows[row]][1] , league_stats_sd))

            except:
                continue
        print('...')

    stats_show = ['2018-19', 'Pos','PLAYER', 'TEAM',  'PTS', 'FG%', 'REB', 'AST', 'STL', 'BLK',  'FT%','3P%', 'TOV',  'FOUL', 'MINS', 'FGA']

    print('Trade Base Ideas:')
    for trade in range(5):
        print((trade + 1),'.', trades[trade + 1][0], 'for', trades[trade + 1][1], '. Cap Change:',trades[trade + 1][5]/1000000, 'M', '. Trade Score:', trades[trade + 1][2])

        player1_stats = show_player_stats(player_stats, trades[trade + 1][0])
        player2_stats = show_player_stats(player_stats, trades[trade + 1][1])

        print(team_name, 'Weakest Areas: ', team_weakness)
        for stat in range(len(player1_stats)):
            for stat_shown in range(len(stats_show)):
                if player_stats[0][stat] == stats_show[stat_shown]:
                    print(player_stats[0][stat], player2_stats[stat])
        print('Salary', trades[trade + 1][4]/1000000, 'M')


        print('...')

        print(player2_stats[1], 'Weakest Areas: ',find_w_s(team_stats, league_stats_projected_avg, player2_stats[1] , league_stats_sd))
        for stat in range(len(player2_stats)):
            for stat_shown in range(len(stats_show)):
                if player_stats[0][stat] == stats_show[stat_shown]:
                    print(player_stats[0][stat], player1_stats[stat])
        print('Salary', trades[trade + 1][3]/1000000,'M ')


        print('...')
        print('...')
        print('...')

def run(file, year, team_name, player_type, max_cap_hit):
    player_stats, league_stats, team_stats, sal_stats, pos_stats = int_data(file)
    league_stats_projected_avg, league_stats_sd = project_stats(league_stats, year)
    fit_ratings = find_best_fit(league_stats_sd, league_stats_projected_avg, team_name, team_stats, player_stats, pos_stats, player_type)
    team_weakness = find_w_s(team_stats, league_stats_projected_avg, team_name, league_stats_sd)
    trades = find_trade(fit_ratings, team_stats, player_stats, league_stats_sd, league_stats_projected_avg, team_name, sal_stats, max_cap_hit, pos_stats, player_type)
    display(team_weakness, fit_ratings, team_stats, player_stats, team_name, file, trades, league_stats_projected_avg, league_stats_sd)

teams = ['MIL', 'TOR', 'GSW', 'DEN', 'HOU', 'POR', 'PHI', 'UTA', 'BOS', 'OKC', 'IND', 'LAC', 'SAS', 'BKN', 'ORL', 'DET', 'CHA', 'MIA', 'SAC', 'LAL', 'MIN', 'DAL', 'MEM', 'NOP', 'WAS', 'ATL', 'CHI', 'PHX', 'NYk']

# run(r'/users/2020jswain/desktop/mball_stat.xlsx', 2019, 'DEN', 'Wing', 10000000)
# run(r'/users/2020jswain/desktop/mball_stat.xlsx', 2019, 'MIL', 'Wing', 10000000)
# run(r'/users/2020jswain/desktop/mball_stat.xlsx', 2019, 'POR', 'Wing', 10000000)



run(r'/users/2020jswain/desktop/mball_stat.xlsx', 2019, 'CHI', 'Wing', 10000000)
# run(r'/users/2020jswain/desktop/mball_stat.xlsx', 2019, 'IND', 'Wing', 10000000)
# run(r'/users/2020jswain/desktop/mball_stat.xlsx', 2019, 'MIL', 'Wing', 10000000)
# run(r'/users/2020jswain/desktop/mball_stat.xlsx', 2019, 'SAS', 'Wing', 10000000)

#
#
#
# for team in teams:
#     print(team)
#     run(r'/users/2020jswain/desktop/mball_stat.xlsx', 2019, team, 'Wing', 10000000)
