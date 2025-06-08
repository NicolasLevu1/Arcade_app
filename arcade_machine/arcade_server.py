from flask import Flask, jsonify, send_from_directory, request, redirect
import time
import subprocess
from datetime import datetime
import json
from collections import defaultdict

# made by nicolas levu
# Flask setup
app = Flask(__name__, static_folder='website')

# Constants
FILE_GAMELIST = "/home/pi/game_selector/random_games.json"
FILE_AUTOSTART = "/opt/retropie/configs/all/autostart.sh"
FILE_COININFO = "/home/pi/coinslot/coin_info.json"

def getGameFullPath(file_name):
    """ Takes the filename of a game and returns the full command for running the game."""
    with open(FILE_GAMELIST, "r") as file:
        data = file.read()
    
    game_list = data["games"]

    for game in game_list:
        if file_name in game:
            return game
        
    print("The game you are trying to access doesn't exist.")
    return None

def getCurrentGameFile():
    """ Returns the file name of the game currently set to run on the machine. """
    with open(FILE_AUTOSTART, "r") as file:
        data = file.read()
    
    try:
        game_path = data.strip()
        game_path = game_path.split("/")[-1] # Get whatever filename follows the last slash
        return game_path
    except:
        return None

# Auto Redirect
@app.route("/connecttest.txt")
@app.route("/generate_204")
@app.route("/204")
@app.route("/ncsi.txt")
@app.route("/redirect")
@app.route("/success.txt")
@app.route("/hotspot-detect.html")
def captive_portal():
    return redirect("/")

# Serve HTML
@app.route('/')
def serve_home():
    return send_from_directory(app.static_folder, 'index.html')

# Serve Images
@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('website/images', filename)

# Serve Javascript
@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('website/js', filename)

# Return current game
@app.route('/current_game')
def get_current_game():
    current_game = getCurrentGameFile()
    
    if current_game != None:
        return jsonify({"current_game": current_game})

    return jsonify({"current_game": "No current game"})

# Set current game name (for internal tools or UI call)
@app.route('/set_game', methods=['POST'])
def set_game():
    data = request.get_json()
    new_game = data.get('game', None)

    # Get the current game that's running
    current_game = getCurrentGameFile()

    # Get full command for new game
    game_command = getGameFullPath(new_game)
    if game_command == None:
        # Throw Error
        return jsonify({"message": "The game you are trying to set doesn't exist."})

    # Rewrite autostart.sh
    with open(FILE_AUTOSTART, "w") as file:
        file.write(game_command + "\n")
    
    # Kill the current game
    if current_game != None:
        subprocess.run(["pkill", "retroarch"])

    # Run the new game
    subprocess.Popen(game_command.split(" "))

    print(f"[*] Game changed to: {new_game}")
    return jsonify({"message": f"Current game set to '{new_game}'"})

# Send stats to frontend
@app.route('/stats')
def stats():
    # The python script controlling the coin slot will track how many coins are inserted
    # for each game in a json file. This function can just return that json file
    # and the browser can use it to create a chart or bar graph.
    with open(FILE_COININFO, "r") as file:
    # with open("arcade_machine/jsont.json", "r") as file:
        original_data = json.load(file)
    combined_data = {}

    for game, values in original_data.items():
        date_totals = defaultdict(int)

        for timestamp in values["times"]:  # Fixed: no zip
            # Extract just the date part (YYYY-MM-DD)
            date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M").date()
            date_totals[str(date)] += 1

        # Sort the dates
        sorted_dates = sorted(date_totals.keys())

        combined_data[game] = {
            "coins": [date_totals[d] for d in sorted_dates],
            "times": sorted_dates
        }

    # Now you can return or save combined_data
    #print(json.dumps(combined_data, indent=2))

    #get a list that takes the dates and combines then into their hours
    return json.dumps(combined_data, indent=2)
'''

    return """
    {
        "Pac-Man": {
            "coins": [3, 2, 5],
            "times": ["2025-05-10 14:30", "2025-05-11 12:15", "2025-05-12 16:45"]
        },
        "Galaga": {
            "coins": [1, 4, 2],
            "times": ["2025-05-10 13:00", "2025-05-11 14:45", "2025-05-13 18:30"]
        },
        "Donkey Kong": {
            "coins": [2, 1, 3, 4],
            "times": ["2025-05-09 11:20", "2025-05-10 15:50", "2025-05-12 17:10", "2025-05-14 20:00"]
        }
    }
    """
    '''

# Reboot the machine
@app.route('/reboot', methods=['POST'])
def reboot():
    try:
        subprocess.run(["sudo", "reboot"], check=True)
        return jsonify({"message": "Reboot started"})
    
    except subprocess.CalledProcessError as e:
        print("Failed to reboot system: " + e)
        return jsonify({"message": "Reboot failed"})

# Get the current time on the machine
@app.route('/system_time')
def get_system_time():
    return jsonify({
        "time": time.time()
    })

# Update the system time
@app.route('/change_time', methods=['POST'])
def change_time():
    data = request.get_json()
    new_time = data.get('time', None)

    if new_time == None:
        return jsonify({"message": "Failed to change system time"})
    
    # Format new_time to be a string
    new_time = datetime.fromtimestamp(new_time)
    new_time = new_time.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        subprocess.run(["sudo", "timedatectl", "set-ntp", "false"], check=True)
        subprocess.run(["sudo", "timedatectl", "set-time", new_time], check=True)
        subprocess.run(["sudo", "timedatectl", "set-ntp", "true"], check=True)

    except subprocess.CalledProcessError as e:
        print("failed to change system time: " + e)
        return jsonify({"message": "Failed to change system time"})

    return jsonify({"message": "Changed system time"})

# Start server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
