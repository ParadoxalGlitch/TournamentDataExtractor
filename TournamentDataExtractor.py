import sys
import xml.etree.ElementTree as ET
from datetime import datetime

if len(sys.argv) < 2:
    print("Please drag and drop a tournament file into the program")
    sys.exit(1)

# Get first argument as file path
file_path = sys.argv[1]

# Load XML (or any file type) as long as it is in XML format
with open(file_path, "r", encoding="utf-8") as file:
    tree = ET.parse(file)
    root = tree.getroot()

# Get tournament type (not final)
tournament_type = root.attrib['type']

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
            time = match.find('timestamp').text if match.find('timestamp') is not None else "Unkown"
            timestamp = time.split()[0] # Takes only the date from the timestamp

            # Date format conversion
            timestamp_converted = datetime.strptime(timestamp, "%m/%d/%Y")
            timestamp_converted = timestamp_converted.strftime("%d/%m/%Y")

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
                "timestamp_converted": timestamp_converted

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
        lastname2 = lastnames[1] 

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
for player in standings.findall(".//player[@place]"):
    place = player.attrib['place']
    user_id = player.attrib['id']
    podium.append({"place": place, "name": user_id})

# Order the podium by place
podium = sorted(podium, key=lambda x: int(x['place']))

# Store all the individual matchup in the output file
with open('individual_matchups.txt', 'w', encoding="utf-8") as file:
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
        file.write(f"{matchup['timestamp_converted']}\n")

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
        file.write(f"{matchup['timestamp_converted']}\n")


# Store all the player data in the output file
with open('players_info.txt', 'w', encoding="utf-8") as file:
    for player in players:
        file.write(f"{player['player_id']}\t{player['firstname']}\t{player['lastname1']}\t{player['lastname2']}\t{player['firstname']} {player['lastname1']}\n")


# Prints top 4
print("\nPodio:")
for place in podium[:4]:
    print(place)
