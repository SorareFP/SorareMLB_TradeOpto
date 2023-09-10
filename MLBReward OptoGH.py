import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpBinary
from itertools import combinations
from copy import deepcopy

# Contest specifications
contests = [
    {'name': 'Common Pickup', 'scarcity': 'Common', 'constraint': 'pickup', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
    {'name': 'Common Contender', 'scarcity': 'Common', 'constraint': 'contender', 'zero_highest_l10': False, 'player_count': 5, 'L10_limit': 110},
    {'name': 'Common Eastern Conference', 'scarcity': 'Common', 'constraint': 'conference', 'zero_highest_l10': True, 'conference': 'E',
     'player_count': 5, 'L10_limit': 120},
    {'name': 'Common Western Conference', 'scarcity': 'Common', 'constraint': 'conference', 'zero_highest_l10': True, 'conference': 'W',
     'player_count': 5, 'L10_limit': 120},
{'name': 'Common U23', 'scarcity': 'Common', 'constraint': 'age', 'age_constraint': 'U23', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
    {'name': 'Common Veterans', 'scarcity': 'Common', 'constraint': 'age', 'age_constraint': 'Veterans', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Common No Cap', 'scarcity': 'Common', 'constraint': 'pickup', 'player_count': 5, 'zero_highest_l10': False, 'L10_limit': None},
{'name': 'Common Underdog', 'scarcity': 'Common', 'constraint': 'pickup', 'player_count': 5, 'zero_highest_l10': False, 'L10_limit': 60},
    {'name': 'Limited Champion', 'scarcity': 'Limited', 'constraint': 'champion', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
    {'name': 'Limited Contender', 'scarcity': 'Limited', 'constraint': 'contender', 'zero_highest_l10': False, 'player_count': 5, 'L10_limit': 110},
    {'name': 'Limited Eastern Conference', 'scarcity': 'Limited', 'constraint': 'conference', 'zero_highest_l10': True, 'conference': 'E',
     'player_count': 5, 'L10_limit': 120},
    {'name': 'Limited Western Conference', 'scarcity': 'Limited', 'constraint': 'conference', 'zero_highest_l10': True, 'conference': 'W',
     'player_count': 5, 'L10_limit': 120},
{'name': 'Limited U23', 'scarcity': 'Limited', 'constraint': 'age', 'age_constraint': 'U23', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
    {'name': 'Limited Veterans', 'scarcity': 'Limited', 'constraint': 'age', 'age_constraint': 'Veterans', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Limited No Cap', 'scarcity': 'Limited', 'constraint': 'no cap', 'zero_highest_l10': False, 'player_count': 5, 'L10_limit': None},
{'name': 'Limited Underdog', 'scarcity': 'Limited', 'constraint': 'underdog', 'zero_highest_l10': False, 'player_count': 5, 'L10_limit': 60},
    {'name': 'Rare Champion', 'scarcity': 'Rare', 'constraint': 'champion', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
    {'name': 'Rare Contender', 'scarcity': 'Rare', 'constraint': 'contender', 'zero_highest_l10': False, 'player_count': 5, 'L10_limit': 110},
    {'name': 'Rare Eastern Conference', 'scarcity': 'Rare', 'constraint': 'conference', 'zero_highest_l10': True, 'conference': 'E',
     'player_count': 5, 'L10_limit': 120},
    {'name': 'Rare Western Conference', 'scarcity': 'Rare', 'constraint': 'conference', 'zero_highest_l10': True, 'conference': 'W',
     'player_count': 5, 'L10_limit': 120},
{'name': 'Rare U23', 'scarcity': 'Rare', 'constraint': 'age', 'age_constraint': 'U23', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
    {'name': 'Rare Veterans', 'scarcity': 'Rare', 'constraint': 'age', 'age_constraint': 'Veterans', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Rare No Cap', 'scarcity': 'Rare', 'constraint': 'no cap', 'player_count': 5, 'zero_highest_l10': False, 'L10_limit': None},
{'name': 'Rare Underdog', 'scarcity': 'Rare', 'constraint': 'underdog', 'player_count': 5, 'zero_highest_l10': False, 'L10_limit': 60},
    {'name': 'Super Rare Champion', 'scarcity': 'Super Rare', 'constraint': 'champion', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
    {'name': 'Super Rare Contender', 'scarcity': 'Super Rare', 'constraint': 'contender', 'zero_highest_l10': False, 'player_count': 5, 'L10_limit': 110},
    {'name': 'Super Rare Eastern Conference', 'scarcity': 'Super Rare', 'constraint': 'conference', 'zero_highest_l10': True, 'conference': 'E',
     'player_count': 5, 'L10_limit': 120},
    {'name': 'Super Rare Western Conference', 'scarcity': 'Super Rare', 'constraint': 'conference', 'zero_highest_l10': True, 'conference': 'W',
     'player_count': 5, 'L10_limit': 120},
{'name': 'Super Rare U23', 'scarcity': 'Super Rare', 'constraint': 'age', 'age_constraint': 'U23', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
    {'name': 'Super Rare Veterans', 'scarcity': 'Super Rare', 'constraint': 'age', 'age_constraint': 'Veterans', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Super Rare No Cap', 'scarcity': 'Super Rare', 'constraint': 'no cap', 'zero_highest_l10': False, 'player_count': 5, 'L10_limit': None},
{'name': 'Super Rare Underdog', 'scarcity': 'Super Rare', 'constraint': 'underdog', 'zero_highest_l10': False, 'player_count': 5, 'L10_limit': 60},
{'name': 'Unique Champion', 'scarcity': 'Unique', 'constraint': 'champion', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
    {'name': 'Unique Contender', 'scarcity': 'Unique', 'constraint': 'contender', 'zero_highest_l10': False, 'player_count': 5, 'L10_limit': 110},
    {'name': 'Unique Eastern Conference', 'scarcity': 'Unique', 'constraint': 'conference', 'zero_highest_l10': True, 'conference': 'E',
     'player_count': 5, 'L10_limit': 120},
    {'name': 'Unique Western Conference', 'scarcity': 'Unique', 'constraint': 'conference', 'zero_highest_l10': True, 'conference': 'W',
     'player_count': 5, 'L10_limit': 120},
{'name': 'Unique U23', 'scarcity': 'Unique', 'constraint': 'age', 'age_constraint': 'U23', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
    {'name': 'Unique Veterans', 'scarcity': 'Unique', 'constraint': 'age', 'age_constraint': 'Veterans', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Unique No Cap', 'scarcity': 'Unique', 'constraint': 'no cap', 'zero_highest_l10': False, 'player_count': 5, 'L10_limit': None},
{'name': 'Unique Underdog', 'scarcity': 'Unique', 'constraint': 'underdog', 'zero_highest_l10': False, 'player_count': 5, 'L10_limit': 60},
{'name': 'Common All-Offense', 'scarcity': 'Common', 'constraint': 'All-Offense', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Limited All-Offense', 'scarcity': 'Limited', 'constraint': 'All-Offense', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Rare All-Offense', 'scarcity': 'Rare', 'constraint': 'All-Offense', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Super Rare All-Offense', 'scarcity': 'Super Rare', 'constraint': 'All-Offense', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Unique All-Offense', 'scarcity': 'Unique', 'constraint': 'All-Offense', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Common All-Defense', 'scarcity': 'Common', 'constraint': 'All-Defense', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Limited All-Defense', 'scarcity': 'Limited', 'constraint': 'All-Defense', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Rare All-Defense', 'scarcity': 'Rare', 'constraint': 'All-Defense', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Super Rare All-Defense', 'scarcity': 'Super Rare', 'constraint': 'All-Defense', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
{'name': 'Unique All-Defense', 'scarcity': 'Unique', 'constraint': 'All-Defense', 'zero_highest_l10': True, 'player_count': 5, 'L10_limit': 120},
]

# Assuming you've already retrieved the player data from the Sorare API
# For demonstration purposes, I'm using a sample dataframe
player_data = pd.read_excel('C:/Users/hoops/OneDrive/Documents/Sorare/SorareNBA1.xlsm', sheet_name='My Gallery')
# Dictionary specifying which columns should have NaNs replaced by 0s
columns_to_fill = {'Team': 'None', 'age': 'None', 'Median': 0, 'Best Game': 0, 'UpPtsAdded': 0}
# Apply fillna only on the specified columns
player_data.fillna(value=columns_to_fill, inplace=True)


def build_lineup(player_data, contest, selected_players_names=None):
    if selected_players_names is None:
        selected_players_names = []

    selected_players = []
    player_count = contest.get('player_count', 5)  # Assuming default of 5 if not specified

    numeric_columns = ['UpPtsAdded', 'age', 'L10', 'Upside', 'Best Game', 'All-Off', 'All-Def']
    player_data[numeric_columns] = player_data[numeric_columns].apply(pd.to_numeric, errors='coerce')

    # Filter out rows where L10 is NaN
    player_data = player_data[player_data['L10'].notna()]

    filtered_players = player_data[player_data['scarcity'] == contest['scarcity']]

    # Remove already selected players
    filtered_players = filtered_players[~filtered_players['name'].isin(selected_players_names)]

    # Sorting column based on contest constraint
    if contest['constraint'] == 'All-Offense':
        sort_column = 'All-Off'
    elif contest['constraint'] == 'All-Defense':
        sort_column = 'All-Def'
    else:
        sort_column = 'UpPtsAdded'

    filtered_players = filtered_players.sort_values(by=sort_column, ascending=False)

    # Apply age constraint if specified
    if 'age_constraint' in contest:
        if contest['age_constraint'] == 'U23':
            filtered_players = filtered_players[filtered_players['age'] <= 23]
        elif contest['age_constraint'] == 'Veterans':
            filtered_players = filtered_players[filtered_players['age'] >= 30]

    # Apply conference constraint if specified
    if 'conference' in contest:
        if contest['conference'] == 'E':
            filtered_players = filtered_players[filtered_players['conference'] == 'E']
        elif contest['conference'] == 'W':
            filtered_players = filtered_players[filtered_players['conference'] == 'W']

    print(f"Number of players left: {len(filtered_players)}")

    numeric_columns = ['UpPtsAdded', 'age', 'L10', 'Upside', 'Best Game', 'All-Off', 'All-Def']
    player_data[numeric_columns] = player_data[numeric_columns].apply(pd.to_numeric, errors='coerce')

    player_data = player_data[player_data['L10'].notna()]
    filtered_players = player_data[player_data['scarcity'] == contest['scarcity']]
    filtered_players = filtered_players[~filtered_players['name'].isin(selected_players_names)]

    # First Linear Programming Optimization (for the first n-2 players based on UpPtsAdded)
    player_vars = LpVariable.dicts("Player", filtered_players.index, 0, 1, LpBinary)
    objective = sum(filtered_players.loc[i, sort_column] * player_vars[i] for i in filtered_players.index)

    prob = LpProblem("LineupOptimization_Step1", LpMaximize)
    prob += objective
    prob += sum(player_vars[i] for i in filtered_players.index) == player_count - 2  # n-2 players
    prob.solve()

    first_batch_selected = []
    for i in filtered_players.index:
        if player_vars[i].value() == 1:
            selected_player = deepcopy(filtered_players.loc[i].to_dict())
            first_batch_selected.append(selected_player)
            selected_players.append(selected_player)

    # Remove selected players for the second optimization
    selected_indices = [player['name'] for player in first_batch_selected]
    filtered_players = filtered_players[~filtered_players['name'].isin(selected_indices)]

    if contest.get('zero_highest_l10', True):

        # Create all possible pairs of the remaining players, sorted by combined Upside
        remaining_player_pairs = list(combinations(filtered_players.index, 2))
        remaining_player_pairs.sort(
            key=lambda x: filtered_players.loc[x[0], 'Upside'] + filtered_players.loc[x[1], 'Upside'], reverse=True)

        for player1_idx, player2_idx in remaining_player_pairs:
            player1 = deepcopy(filtered_players.loc[player1_idx].to_dict())
            player2 = deepcopy(filtered_players.loc[player2_idx].to_dict())
            potential_lineup = first_batch_selected + [player1, player2]

            # Try zeroing out highest L10 player and checking if the limit is exceeded
            potential_lineup = first_batch_selected + [player1, player2]
            highest_l10_player = max(potential_lineup, key=lambda x: x['L10'])
            temp_l10 = highest_l10_player['L10']
            highest_l10_player['L10'] = 0  # Temporarily zero out

            total_l10 = sum(player['L10'] for player in potential_lineup)

            # If within L10_limit, we're done
            if 'L10_limit' in contest and total_l10 <= contest['L10_limit']:
                highest_l10_player['L10'] = temp_l10  # Revert back to original L10
                highest_l10_player['L10'] = 0  # Officially zero out
                selected_players += [player1, player2]
                break

            highest_l10_player['L10'] = temp_l10  # Revert back to original L10 if the lineup didn't work

    else:
        # Maximize for the first n-2 players, then substitute as you described
        initial_candidates = sorted(filtered_players.to_dict('records'), key=lambda x: x[sort_column], reverse=True)[:2]

        potential_lineup = first_batch_selected + initial_candidates
        total_l10 = sum(player['L10'] for player in potential_lineup)
        if 'L10_limit' in contest and total_l10 > contest['L10_limit']:
            # If the initial lineup exceeds L10_limit, then skip the following logic and go directly to calculating total points
            pass
        else:
            # Step 2: Iterate to find better lineups
            for _ in range(5):  # Repeat up to 5 times
                min_upside_player = min(potential_lineup, key=lambda x: x['Upside'])
                # Create a pool of potential replacements
                potential_replacements = [player for player in filtered_players.to_dict('records') if
                                          player not in potential_lineup]
                # Sort potential replacements by Upside and filter those that don't exceed L10 limit
                potential_replacements = sorted(
                    [player for player in potential_replacements if
                     total_l10 - min_upside_player['L10'] + player['L10'] <= contest['L10_limit']],
                    key=lambda x: x['Upside'], reverse=True
                )
                # If a better replacement exists, update lineup and total_l10
                if potential_replacements and potential_replacements[0]['Upside'] > min_upside_player['Upside']:
                    potential_lineup.remove(min_upside_player)
                    potential_lineup.append(potential_replacements[0])
                    total_l10 = total_l10 - min_upside_player['L10'] + potential_replacements[0]['L10']
            selected_players += potential_lineup[-2:]  # Add the newly selected players (index 3 and 4) to the lineup
    # Calculate total points
    total_points = sum(player['UpPtsAdded'] for player in selected_players)
    return selected_players, total_points

def main():
    selected_players = {}  # Dictionary to store selected players for each contest
    selected_contest = None  # Initialize selected_contest outside the loop
    selected_players_names = []  # Initialize selected_players_names list

    while True:
        go_back_to_scarcity = False  # Flag to indicate whether to return to the scarcity selection

        print("Select Scarcity:")
        for i, scarcity in enumerate(['Common', 'Limited', 'Rare', 'Super Rare', 'Unique'], start=1):
            print(f"{i}. {scarcity}")

        try:
            selected_scarcity_idx = int(input("Enter the number of the scarcity you want (or 0 to exit): ")) - 1

            if selected_scarcity_idx == -1:
                break

            if 0 <= selected_scarcity_idx < len(['Common', 'Limited', 'Rare', 'Super Rare', 'Unique']):
                selected_scarcity = ['Common', 'Limited', 'Rare', 'Super Rare', 'Unique'][selected_scarcity_idx]

                while True:
                    available_contests = [contest for contest in contests if contest['scarcity'] == selected_scarcity]

                    print(f"Available {selected_scarcity} Contests:")
                    for i, contest in enumerate(available_contests, start=1):
                        print(f"{i}. {contest['name']}")

                    try:
                        selected_contest_idx = int(input("Enter the number of the contest you want to build a lineup for (or 0 to go back): ")) - 1

                        if selected_contest_idx == -1:
                            break  # Go back to Scarcity selection

                        if 0 <= selected_contest_idx < len(available_contests):
                            selected_contest = available_contests[selected_contest_idx]

                            # Check if there's an existing lineup for this contest
                            if selected_contest['name'] in selected_players:
                                overwrite = input("You already have a lineup for this contest. Do you want to overwrite it? (y/n): ")
                                if overwrite.lower() == 'y':
                                    selected_players[selected_contest['name']] = set()
                                else:
                                    continue  # Go back to Contest selection
                            else:
                                selected_players[selected_contest['name']] = set()  # Initialize the set

                            selected_players_names = set()  # Initialize selected_players_names for this contest

                            # Build and display lineup
                            lineup, total_points = build_lineup(player_data, selected_contest, selected_players_names)

                            # Print lineup details (same as before)
                            print(f"Lineup for {selected_contest['name']}:")
                            total_l10 = sum(player['L10'] for player in lineup)
                            total_upside = sum(player['Upside'] for player in lineup)
                            median_best_game = sum(player['Best Game'] for player in lineup)

                            for player in lineup:
                                print(
                                    f"{player['name']}, ({player['UpPtsAdded']:.2f} points added, {player['L10']:.2f} L10)")
                            print(f"Total points added: {total_points:.2f}")
                            print(f"Total L10: {total_l10:.2f}/{selected_contest['L10_limit']}")
                            print(f"Total Upside: {total_upside:.2f}")
                            print(f"Median Best Game: {median_best_game:.2f}")

                            # Add selected players to the set for this contest
                            selected_players[selected_contest['name']] = {player['name'] for player in lineup}

                            # Prompt to build another lineup
                            another_lineup = input("Do you want to build another lineup? (y/n): ")
                            if another_lineup.lower() == 'y':
                                go_back_to_scarcity = True  # Set flag to True
                                break  # Exit the Contest loop
                            else:
                                break  # Exit the Contest loop, but keep flag as False

                    except ValueError:
                        print("Invalid input for contest selection. Please enter a valid number.")

        except ValueError:
            print("Invalid input for scarcity selection. Please enter a valid number.")

if __name__ == "__main__":
    main()
