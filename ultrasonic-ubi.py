import RPi.GPIO as GPIO
import time
import requests

# Konfigurasi pin GPIO
TRIG_PIN = 18
ECHO_PIN = 24

# Konfigurasi Ubidots
UBIDOTS_TOKEN = "BBFF-2jXFcArgZADJPrXdNDezHs4Q95gudr"
DEVICE_LABEL = "ultrasonic"  # Ganti dengan label device yang Anda buat di Ubidots

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def get_distance():
    # Mengirimkan pulse ke pin TRIG selama 10us
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    # Mencatat waktu saat pulsa dikirim dan diterima kembali
    pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    pulse_end = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    # Menghitung durasi pulsa
    pulse_duration = pulse_end - pulse_start

    # Menghitung jarak berdasarkan durasi pulsa dan kecepatan suara
    speed_of_sound = 34300  # Kecepatan suara dalam cm/s
    distance = (pulse_duration * speed_of_sound) / 2

    return distance

def send_distance_to_ubidots(distance):
    url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}

    payload = {
        "distance": distance
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("Distance data successfully sent to Ubidots")
        else:
            print("Failed to send distance data to Ubidots")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    try:
        while True:
            distance = get_distance()
            print(f"Distance: {distance:.2f} cm")
            send_distance_to_ubidots(distance)
            time.sleep(0.1)  # Ubah angka 1 ke interval yang diinginkan (dalam detik)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Terminated by the user")