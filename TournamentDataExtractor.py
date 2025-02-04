import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox


# Function that the display uses to get input from the user
def process_input():
    global store, tournament_type
    store = store_entry.get()
    tournament_type = tournament_type_entry.get()
    print("changed everything")
    
    if not store or not tournament_type:
        messagebox.showwarning("No empty values are allowed")
        return

    overlay.destroy()




if len(sys.argv) < 2:
    print("Please drag and drop a tournament file into the program")
    sys.exit(1)

# Get first argument as file path
file_path = sys.argv[1]

# Load XML (or any file type) as long as it is in XML format
with open(file_path, "r", encoding="utf-8") as file:
    tree = ET.parse(file)
    root = tree.getroot()

# Create output files folder if not exixts
os.makedirs('output_files', exist_ok=True)


# Create log file
log_file = open("output_files/log_file.txt", "a")

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.write(f"[{timestamp}] {message}\n")
    log_file.flush()


# Create the input window
overlay = tk.Tk()
overlay.title("Tournament Data Extractor")

# Create the "store" input
tk.Label(overlay, text="Store:").grid(row=0, column=0)
store_entry = tk.Entry(overlay)
store_entry.grid(row=0, column=1)

# Create the "tournament_type" input
tk.Label(overlay, text="Tournament type:").grid(row=1, column=0)
tournament_type_entry = tk.Entry(overlay)
tournament_type_entry.grid(row=1, column=1)

# Create the "Confirm" button
tk.Button(overlay, text="Confirm", command=process_input).grid(row=2, column=0, columnspan=2)

# Displays the window
overlay.mainloop()


# Get tournament date
data_node = root.find(".//data")
tournament_date = data_node.find('startdate').text if data_node.find('startdate') is not None else "Unknown"

# Date format conversion
td_converted = datetime.strptime(tournament_date, "%m/%d/%Y")
td_converted = td_converted.strftime("%d/%m/%Y")

# Get every matchups
matchups = []
for round_node in root.findall(".//round"):

    if 'number' in round_node.attrib:
        round_number = round_node.attrib['number'] # Round number

        for match in round_node.findall(".//match"):

            # Get match data
            outcome = match.attrib.get('outcome') 
            player1_node = match.find('player1')
            player2_node = match.find('player2')
            table_number = match.find('tablenumber').text if match.find('tablenumber') is not None else "Unknown"

            # Obtain player IDs
            if outcome in ('5', '8'):
                player1_id = match.find('player').attrib.get('userid') if match.find('player') is not None else "Unknown"
                if outcome == '5':
                    player2_id = 0 # Bye 
                else:
                    player2_id = 99 # Not shown
            else:
                player1_id = player1_node.attrib['userid']
                player2_id = player2_node.attrib['userid']

            # Matchup data structure
            matchup = {
                "round": round_number,
                "table": table_number,
                "player1": player1_id, 
                "player2": player2_id, 
                "outcome": outcome,
                "tournament_date": td_converted,
            }
            matchups.append(matchup)
    else:
        print(f"Ignoring node {ET.tostring(round_node)}, not a match node, but a match drop node")



# Get player information

players = []
players_node = root.findall(".players")

for player_info in players_node[0].findall(".player"):

    player_id = player_info.attrib.get('userid')
    firstname = player_info.find('firstname').text
    lastname = player_info.find('lastname').text
    lastnames = lastname.split()

    if len(lastnames) == 1:
        lastname1 = lastnames[0]
        lastname2 = ' '
    else:
        lastname1 = lastnames[0]
        lastname2 = " ".join(lastnames[1:])

    player = {
        "player_id": player_id,
        "firstname": firstname,
        "lastname1": lastname1, 
        "lastname2": lastname2, 
    }
    
    players.append(player)





# Get the podium
standings = root.find(".//standings")
podium = []

if (standings is not None):
    for player in standings.findall(".//player[@place]"):
        place = player.attrib['place']
        player_id = player.attrib['id']

        podium_pos = {
            "player_id": player_id,
            "tournament_date": td_converted,
            "tournament_type": tournament_type,
            "place": place,
        }

        podium.append(podium_pos)

else:
    log_message("No standings found")



# Store all the individual matchup in the output file
with open('output_files/players_rounds.txt', 'w', encoding="utf-8") as file:
    for matchup in matchups:
        # Player 1
        file.write(f"{matchup['player1']}\t{matchup['table']}\t{matchup['round']}\t")
        if matchup['outcome'] == '1':
            file.write(f"1\t")
        elif matchup['outcome'] == '2':
            file.write(f"2\t")
        elif matchup['outcome'] == '3':
            file.write(f"3\t")
        elif matchup['outcome'] == '5':
            file.write(f"1\t")
        elif matchup['outcome'] == '8':
            file.write(f"1\t")

        file.write(f"{tournament_type}\t")
        file.write(f"{matchup['tournament_date']}\t")
        file.write(f"{store}\n")

        # Player 2
        file.write(f"{matchup['player2']}\t{matchup['table']}\t{matchup['round']}\t")
        if matchup['outcome'] == '1':
            file.write(f"2\t")
        elif matchup['outcome'] == '2':
            file.write(f"1\t")
        elif matchup['outcome'] == '3':
            file.write(f"3\t")
        elif matchup['outcome'] == '5': # player2 outcome in "bye" matches is a loss
            file.write(f"2\t")
        elif matchup['outcome'] == '8': # player2 outcome in "no show" matches is a loss
            file.write(f"2\t")


        file.write(f"{tournament_type}\t")
        file.write(f"{matchup['tournament_date']}\t")
        file.write(f"{store}\n")


# Store all the player data in the output file
with open('output_files/players_info.txt', 'w', encoding="utf-8") as file:
    for player in players:
        file.write(f"{player['player_id']}\t{player['firstname']}\t{player['lastname1']}\t{player['lastname2']}\t{player['firstname']} {player['lastname1']}\n")

# Store all the podium data (standings) in the output file
if podium:
    with open('output_files/standings.txt', 'w', encoding="utf-8") as file:
        for podium_pos in podium:
            file.write(f"{podium_pos['player_id']}\t{podium_pos['tournament_date']}\t{podium_pos['tournament_type']}\t{podium_pos['place']}\n")

with open('output_files/matchups.txt', 'w', encoding="utf-8") as file:
    for matchup in matchups:
        # Player 1
        file.write(f"{matchup['player1']}\t")
        if matchup['outcome'] == '1':
            file.write(f"1\t")
        elif matchup['outcome'] == '2':
            file.write(f"2\t")
        elif matchup['outcome'] == '3':
            file.write(f"3\t")
        elif matchup['outcome'] == '5':
            file.write(f"1\t")
        elif matchup['outcome'] == '8':
            file.write(f"1\t")

        # Player 2
        file.write(f"{matchup['player2']}\t")
        if matchup['outcome'] == '1':
            file.write(f"2\t")
        elif matchup['outcome'] == '2':
            file.write(f"1\t")
        elif matchup['outcome'] == '3':
            file.write(f"3\t")
        elif matchup['outcome'] == '5': # player2 outcome in "bye" matches is a loss
            file.write(f"2\t")
        elif matchup['outcome'] == '8': # player2 outcome in "no show" matches is a loss
            file.write(f"2\t")


        file.write(f"{tournament_type}\t")
        file.write(f"{td_converted}\t")
        file.write(f"{matchup['round']}\t")
        file.write(f"{store}\n")


file.close()
log_file.close()
# Prints end of program
print("\nEnd of program")

