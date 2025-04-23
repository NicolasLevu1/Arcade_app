from flask import Flask, jsonify, send_from_directory, request
import RPi.GPIO as GPIO
import time

# Create the Flask app and point it to the static website folder
app = Flask(__name__, static_folder='website')

# Coin counter
coins = 0
start_time = time.time()

# GPIO setup
COIN_PIN = 17  # Adjust to match your physical GPIO wiring

GPIO.setmode(GPIO.BCM)
GPIO.setup(COIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def coin_inserted(channel):
    global coins
    coins += 1
    print(f"[+] Coin inserted! Total: {coins}")

GPIO.add_event_detect(COIN_PIN, GPIO.FALLING, callback=coin_inserted, bouncetime=300)

# Serve the arcade dashboard
@app.route('/')
def serve_home():
    return send_from_directory(app.static_folder, 'index.html')

# Send current stats to the frontend
@app.route('/stats')
def stats():
    uptime = round(time.time() - start_time)
    return jsonify({
        "coins": coins,
        "uptime": uptime
    })

# Reset coins via a button click
@app.route('/reset', methods=['POST'])
def reset():
    global coins, start_time
    coins = 0
    start_time = time.time()
    print("[*] Coin counter reset.")
    return jsonify({"message": "Coin counter reset"})

# Start the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
