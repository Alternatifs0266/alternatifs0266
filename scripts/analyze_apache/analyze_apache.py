import re
import requests
from collections import Counter

# --- CONFIGURATION ---
LOG_FILE = "access.log"  # Chemin vers votre fichier log Apache
API_URL = "http://ip-api.com/json/"

def analyze_logs():
    try:
        with open(LOG_FILE, "r") as f:
            log_content = f.read()
            
        # 1. Extraction des adresses IP (Format standard en début de ligne)
        ips = re.findall(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', log_content, re.MULTILINE)
        ip_counts = Counter(ips).most_common(30) # Top 10 des IP les plus actives

        print(f"{'IP Address':<15} | {'Hits':<5} | {'Location':<20}")
        print("-" * 45)

        # 2. Géolocalisation via API
        for ip, count in ip_counts:
            try:
                response = requests.get(f"{API_URL}{ip}?fields=status,country,city").json()
                if response['status'] == 'success':
                    location = f"{response['city']}, {response['country']}"
                else:
                    location = "Unknown"
            except:
                location = "API Error"
            
            print(f"{ip:<15} | {count:<5} | {location:<20}")

    except FileNotFoundError:
        print(f"Erreur : Le fichier {LOG_FILE} est introuvable.")

if __name__ == "__main__":
    analyze_logs()
