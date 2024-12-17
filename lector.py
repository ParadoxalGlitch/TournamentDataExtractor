import sys
import xml.etree.ElementTree as ET

if len(sys.argv) < 2:
    print("Por favor, arrastra un archivo al script.")
    sys.exit(1)

# El primer argumento será el archivo arrastrado
file_path = sys.argv[1]

# Cargar el archivo XML
tree = ET.parse(file_path)
root = tree.getroot()

# Extraer el tipo de torneo
tournament_type = root.attrib['type']

# Extraer los matchups
matchups = []
for round_node in root.findall(".//round"):

    if 'number' in round_node.attrib:
        round_number = round_node.attrib['number']

        for match in round_node.findall(".//match"):

            outcome = match.attrib.get('outcome')
            player1_node = match.find('player1')
            player2_node = match.find('player2')
            table_number = match.find('tablenumber').text if match.find('tablenumber') is not None else "Unknown"
            timestamp = match.find('timestamp').text if match.find('timestamp') is not None else "Unknown"

            if outcome in ('5', '8'):
                player1_id = match.find('player').attrib.get('userid') if match.find('player') is not None else "Unknown"
                player2_id = "none"
            else:
                player1_id = player1_node.attrib['userid']
                player2_id = player2_node.attrib['userid']

            matchup = {
                "round": round_number,
                "table": table_number,
                "player1": player1_id,  # Usamos solo el ID del jugador
                "player2": player2_id,  # Usamos solo el ID del jugador
                "outcome": outcome,
                "timestamp": timestamp
            }
            matchups.append(matchup)
    else:
        print(f"El nodo {ET.tostring(round_node)} no tiene el atributo 'number'")

# Extraer el podio
standings = root.find(".//standings")
podium = []
for player in standings.findall(".//player[@place]"):
    place = player.attrib['place']
    user_id = player.attrib['id']
    podium.append({"place": place, "name": user_id})  # Solo guardamos el ID del jugador

# Ordenar el podio por lugar
podium = sorted(podium, key=lambda x: int(x['place']))

# Guardar los resultados en un archivo de texto
with open('resultados_torneo.txt', 'w') as file:
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
            file.write(f"5\t")
        elif matchup['outcome'] == '8':
            file.write(f"8\t")

        file.write(f"{tournament_type}\n")

        # Player 2
        if (matchup['outcome'] in ('1','2','3')):
            file.write(f"{matchup['player2']}\t{matchup['table']}\t{matchup['round']}\t")
            if matchup['outcome'] == '1':
                file.write(f"2\t")
            elif matchup['outcome'] == '2':
                file.write(f"2\t")
            elif matchup['outcome'] == '3':
                file.write(f"3\t")

            file.write(f"{tournament_type}\n")

# Mostrar el podio
print("\nPodio:")
for place in podium[:3]:  # Top 3
    print(place)
