import requests

def send_command_to_esp(ssid, zone, turn_on):
    try:
        url = f"http://{ssid}/zone/{zone}/"
        action = 'on' if turn_on else 'off'
        response = requests.post(url, json={"action": action}, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print("ESP error:", e)
        return False
