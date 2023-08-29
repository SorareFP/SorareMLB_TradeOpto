import pandas as pd
import unicodedata
import requests
import itertools
from itertools import combinations


# Function to normalize text
def normalize_latin(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')


# Function to match player name and find reward points
def get_reward_sr_pts(player_input, data, sr_pts_column):
    matched_name = normalize_and_match_name(player_input, data.index)
    print("Matched name:", matched_name)

    if matched_name != "Name not found":
        reward_sr_pts = data.loc[matched_name, sr_pts_column]
        return reward_sr_pts, matched_name
    else:
        return None, "Name not found"


# Function to normalize and match player names
def normalize_and_match_name(name, index):
    normalized_input = normalize_latin(name)
    matching_names = index[
        index.str.normalize('NFKD').str.encode('ascii', 'ignore').str.decode('utf-8') == normalized_input]
    if not matching_names.empty:
        return matching_names[0]
    else:
        # Try adding " Jr." to the normalized input and search again
        jr_normalized_input = f"{normalized_input} Jr."
        jr_matching_names = index[
            index.str.normalize('NFKD').str.encode('ascii', 'ignore').str.decode('utf-8') == jr_normalized_input]
        if not jr_matching_names.empty:
            return jr_matching_names[0]
        else:
            return "Name not found"

def generate_combinations(data, original_position, min_players=1, max_players=2):
    combinations = []
    for i in range(min_players, max_players + 1):
        for combo in itertools.combinations(data.iterrows(), i):
            positions = [row[1]['Position'] for _, row in combo]
            if original_position in positions and positions.count('RP') <= 1:  # Add RP constraint here
                combinations.append(combo)
    return combinations


# Function to provide recommendations
def provide_recommendations(data, reward_sr_pts, reward_name, original_position, price_column, sr_pts_column):
    # Work on a copy to avoid modifying original DataFrame
    data = data.copy()

    # Drop NaNs from important columns
    data.dropna(subset=[price_column, sr_pts_column], inplace=True)

    # Convert price column to numeric values
    data[price_column] = pd.to_numeric(data[price_column], errors='coerce')

    # Drop NaNs again, if any are introduced during conversion
    data.dropna(subset=[price_column, sr_pts_column], inplace=True)

    # Proceed with your logic
    valid_sr_pts_rows = data[sr_pts_column] >= reward_sr_pts * 0.8

    # Set valid_price_rows after data cleaning and conversion
    valid_price_rows = data[price_column] <= data.loc[reward_name, price_column]

    # Data Check
    data[price_column] = pd.to_numeric(data[price_column], errors='coerce')

    # Type Check
    print(type(data.loc[reward_name, price_column]))
    print(data[price_column].dtype)

    # Your existing code for valid_price_rows and beyond
    valid_price_rows = data[price_column] <= data.loc[reward_name, price_column]

    # Combining the conditions
    eligible_players = data[
        valid_price_rows &
        valid_sr_pts_rows
        ]

    print(f"Debug: Number of eligible players: {len(eligible_players)}")  ### DEBUG STEP 6: Check Eligible Players

    # Sorting and picking the top
    recommended_players = eligible_players.sort_values(by=sr_pts_column, ascending=False).head(5)

    # Limit to unique recommended players, and only top 5
    unique_recommended_players = recommended_players.drop_duplicates(subset=[sr_pts_column, price_column]).head(5)

    print(f"Debug: Number of unique recommended players: {len(unique_recommended_players)}")

    if len(unique_recommended_players) == 0:
        print("No suitable players found for trading.")
        return
    else:
        def fetch_eth_to_usd():
            url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
            response = requests.get(url)
            eth_to_usd = response.json()["ethereum"]["usd"]
            return eth_to_usd

        eth_to_usd_rate = fetch_eth_to_usd()

        # Add a USD column based on the current conversion rate and the specific price_column for this scarcity level
        recommended_players["USD"] = recommended_players[price_column] * eth_to_usd_rate

        # Print Reward Player Information
        reward_info = data.loc[reward_name]
        print(
            f"Reward: {reward_name} - 'Rest-of-Season Projection:' {reward_info['SR PTS']}, ETH: {reward_info[price_column]}")

        # Helper function for combinations
        def get_combinations(players, min_players=1, max_players=3):
            for r in range(min_players, max_players + 1):
                for combo in combinations(players.iterrows(), r):
                    yield combo

        # Players with higher SR PTS than the reward
        higher_sr_pts_players = data[data[sr_pts_column] > reward_sr_pts]
        higher_sr_pts_players = higher_sr_pts_players.sort_values([sr_pts_column, price_column],
                                                                  ascending=[False, True])
        higher_sr_pts_players.loc[:, 'USD'] = higher_sr_pts_players[price_column] * eth_to_usd_rate

        # Special Recommendation 1: Single best player
        print("\nTop single-player swap:")
        if original_position == 'Hitter':  # Assume 'Hitter' is the designation for hitters
            suitable_players = higher_sr_pts_players[
                (higher_sr_pts_players[price_column] <= reward_info[price_column]) & (
                            higher_sr_pts_players['Position'] == 'Hitter')]
        else:
            suitable_players = higher_sr_pts_players[higher_sr_pts_players[price_column] <= reward_info[price_column]]

        # Check if any suitable players are available
        if not suitable_players.empty:
            best_single_player = suitable_players.iloc[0]
            print(
                f"{best_single_player.name} - SR PTS: {best_single_player[sr_pts_column]}, ETH: {best_single_player[price_column]}, ${best_single_player['USD']:.2f}")
        else:
            print("No suitable players found for trading.")

        # Special Recommendation 2: Best combo of 2-3 cards, all higher SR PTS
        print("\nMultiple player combo (100%+):")
        if original_position == 'Hitter':
            higher_sr_pts_players_filtered = higher_sr_pts_players[higher_sr_pts_players['Position'] == 'Hitter']
        else:
            higher_sr_pts_players_filtered = higher_sr_pts_players
        total_sr_pts_2 = 0
        total_eth_2 = 0
        usd_combo_2 = 0  # Initialize USD variable
        combo_found = False  # Initialize flag to False

        for combo in get_combinations(higher_sr_pts_players_filtered, min_players=2):
            total_price = sum(row[price_column] for _, row in combo)
            total_sr_pts = sum(row[sr_pts_column] for _, row in combo)

            if total_price <= reward_info[price_column] and total_sr_pts > reward_info[sr_pts_column]:
                combo_found = True  # Set flag to True
                total_sr_pts_2 = total_sr_pts
                total_eth_2 = total_price
                usd_combo_2 = sum(row['USD'] for _, row in combo)  # Compute the USD value for the entire combo

                for index, row in combo:
                    print(f"{index} - SR PTS: {row[sr_pts_column]}, ETH: {row[price_column]}, ${row['USD']:.2f}")
                break

        # Check whether a combo was found
        if combo_found:
            print(
                f"Total for Special Recommendation 2: SR PTS: {total_sr_pts_2}, ETH: {total_eth_2}, ${usd_combo_2:.2f}")
        else:
            print("No combo of players project for more points for less than the cost of your reward.")

        # Special Recommendation 3: 2-3 cards, one higher and others 80% or more
        print("\nMultiple player combo (100%+, >=80%):")
        counter_3 = 0  # Add counter for 3 combinations
        total_sr_pts_3 = {}
        total_eth_3 = {}
        usd_3 = {}  # To store USD for each combination
        at_least_80_sr_pts_players = data[data[sr_pts_column] >= 0.8 * reward_sr_pts]
        at_least_80_sr_pts_players = at_least_80_sr_pts_players.copy()
        at_least_80_sr_pts_players["USD"] = at_least_80_sr_pts_players[price_column] * eth_to_usd_rate
        higher_sr_pts_players_filtered = higher_sr_pts_players[higher_sr_pts_players['Position'] == original_position]
        at_least_80_sr_pts_players_filtered = at_least_80_sr_pts_players[
            at_least_80_sr_pts_players['Position'] == original_position]
        for higher in higher_sr_pts_players.iterrows():
            remaining_budget = reward_info[price_column] - higher[1][price_column]
            additional_players = at_least_80_sr_pts_players[
                at_least_80_sr_pts_players[price_column] <= remaining_budget]

            for combo in get_combinations(additional_players, min_players=1, max_players=3):
                if counter_3 >= 3:  # Move the counter check here
                    break

                total_price = higher[1][price_column] + sum(row[price_column] for _, row in combo)
                total_sr_pts = higher[1][sr_pts_column] + sum(row[sr_pts_column] for _, row in combo)
                usd_combo = round(higher[1]['USD'] + sum(row['USD'] for _, row in combo),
                                  2)  # Calculate and round total USD for this combo

                if total_price <= reward_info[price_column] and total_sr_pts > reward_info[sr_pts_column]:
                    combo_id = chr(ord('A') + counter_3)  # 3a, 3b, 3c
                    total_sr_pts_3[combo_id] = total_sr_pts
                    total_eth_3[combo_id] = total_price
                    usd_3[combo_id] = usd_combo

                    print(f"Combo {combo_id}:")
                    print(
                        f"{higher[0]} - SR PTS: {higher[1][sr_pts_column]}, ETH: {higher[1][price_column]}, ${higher[1]['USD']:.2f}")
                    for index, row in combo:
                        print(
                            f"{index} - SR PTS: {row[sr_pts_column]}, ETH: {row[price_column]}, ${row['USD']:.2f}")

                    print(
                        f"Total - SR PTS: {total_sr_pts}, ETH: {total_price}, ${usd_combo:.2f}")  # Print the totals here

                    counter_3 += 1  # Increment counter

            if counter_3 >= 3:  # Additional break to exit the outer loop
                break
        if counter_3 == 0:
            print("No players meet the criteria for a sensible multiple-player swap.")

# Load Data -- THIS WILL BE REPLACED WITH SORARE FP ON FIREBASE
hitter_data = pd.read_excel('(FILEPATH)/SorareMLB.xlsx',
                            sheet_name='Hitter Data')
SP_data = pd.read_excel('(FILEPATH)/SorareMLB.xlsx',
                            sheet_name='SP Data')
RP_data = pd.read_excel('(FILEPATH)/SorareMLB.xlsx',
                            sheet_name='RP Data')

# Remove Shohei Ohtani from SP_data
SP_data.drop("Shohei Ohtani", errors='ignore', inplace=True)  # errors='ignore' ensures the code will not raise an error if the index is not found

# Set index to 'Name'
for data in [hitter_data, SP_data, RP_data]:
    data.set_index('Name', inplace=True)

hitter_data['Position'] = 'Hitter'
SP_data['Position'] = 'SP'
RP_data['Position'] = 'RP'

all_data = pd.concat([hitter_data, SP_data, RP_data])
# Remove Shohei Ohtani from SP_data
SP_data.drop("Shohei Ohtani", errors='ignore', inplace=True)

# Rebuild all_data
all_data = pd.concat([hitter_data, SP_data, RP_data])

# Mapping for price columns based on scarcity
price_column_map = {
    'Limited': 'L Last 3',
    'Rare': 'R Last 3',
    'Super Rare': 'SR Last 3',
    'Unique': 'U Last 3'
}

# Scarcity input and recommendations
def main():
    while True:
        reward_name = input("Enter the name of your reward (or 'exit' to stop): ")
        if reward_name.lower() == 'exit':
            return  # Exit function

        reward_sr_pts, matched_name = get_reward_sr_pts(reward_name, all_data, 'SR PTS')
        if reward_sr_pts is None:
            print("Player not found. Please enter a valid player name.")
            continue  # Skip the rest of the loop and start over

        original_position = all_data.loc[matched_name, 'Position']  # Get the original position of the input player

        while True:  # Inner loop for scarcity selection
            scarcity = input(
                "Select Scarcity:\n1. Common\n2. Limited\n3. Rare\n4. Super Rare\n5. Unique\nEnter the number of the scarcity for your reward (or 0 to exit): ")

            if int(scarcity) == 0:
                return  # Exit function and go back to the outer loop

            try:
                selected_scarcity_idx = int(scarcity) - 1
                selected_scarcity = ['Common', 'Limited', 'Rare', 'Super Rare', 'Unique'][selected_scarcity_idx]
                price_column = price_column_map.get(selected_scarcity, None)

                if price_column:
                    all_data.dropna(subset=[price_column, 'SR PTS'], inplace=True)
                    provide_recommendations(all_data, reward_sr_pts, matched_name, original_position, price_column, 'SR PTS')  # added 'original_position'

                    another_reward = input("Would you like to enter another reward? (y/n): ")
                    if another_reward.lower() == 'y':
                        return main()
                    else:
                        return  # Exit function
                else:
                    print("Invalid scarcity selected. Please choose a valid option.")
            except (ValueError, IndexError):
                print("Invalid input. Please enter a valid number.")

if __name__ == '__main__':
    main()