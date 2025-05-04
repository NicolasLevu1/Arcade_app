from flask import Flask, jsonify, send_from_directory, request
# import RPi.GPIO as GPIO
import time
# made by nicolas levu
# Flask setup
app = Flask(__name__, static_folder='website')

# State variables
coins = 0
current_game = None  # None = no current game
start_time = time.time()

# # GPIO Pins
# COIN_PIN = 17  # Coin acceptor pin

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(COIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# def coin_inserted(channel):
#     global coins
#     coins += 1
#     print(f"[+] Coin inserted! Total: {coins}")

# GPIO.add_event_detect(COIN_PIN, GPIO.FALLING, callback=coin_inserted, bouncetime=300)

# Serve HTML
@app.route('/')
def serve_home():
    return send_from_directory(app.static_folder, 'index.html')

# Serve Images
@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('website/images', filename)

# Return current game (new endpoint)
@app.route('/current_game')
def get_current_game():
    # TODO: add code that reads autostart.sh for the current game.
    return jsonify({
        "current_game": current_game if current_game else "No current game"
    })

# Set current game name (for internal tools or UI call)
@app.route('/set_game', methods=['POST'])
def set_game():
    global current_game
    data = request.get_json()
    current_game = data.get('game', None)
    # TODO: add code that modifies autostart.sh and also kills the current game
    # and runs the new game.
    print(f"[*] Game changed to: {current_game}")
    return jsonify({"message": f"Current game set to '{current_game}'"})

# Send stats to frontend
@app.route('/stats')
def stats():
    # TODO: this entire thing needs to be redone. The way I'm imagining it is that
    # the python script controlling the coin slot will track how many coins are inserted
    # for each game in a json file. Then this function can just return that json file
    # and the browser can use it to create a chart or bar graph.
    uptime = round(time.time() - start_time)
    return jsonify({
        "coins": coins,
        "uptime": uptime
    })

# Reset everything
@app.route('/reset_stats', methods=['POST'])
def reset_stats():
    global coins, current_game, start_time
    coins = 0
    current_game = None
    start_time = time.time()
    return jsonify({"message": "Reset complete"})

# Reboot the machine
@app.route('/reboot', methods=['POST'])
def reboot():
    # TODO: add code to run sudo reboot
    return jsonify({"message": "Reboot complete"})

# Get the current time on the machine
@app.route('/system_time')
def get_system_time():
    return jsonify({
        "time": time.time()
    })

# Start server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
