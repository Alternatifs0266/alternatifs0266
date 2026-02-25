import re
import requests
import ipaddress
from collections import Counter

# --- CONFIGURATION ---
LOG_FILE = "access.log"  # Chemin vers votre fichier log Apache
API_URL = "http://ip-api.com/json/"

def analyze_logs():
    all_ips = []

    try:
        print(f"Analyse du fichier : {LOG_FILE}...")

        # Ouverture du fichier ligne par ligne pour économiser la RAM
        with open(LOG_FILE, "r") as f:
            for line in f:
                # Extraction de l'IP en début de ligne
                match = re.search(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if match:
                    ip_str = match.group(1)

                    try:
                        ip_obj = ipaddress.ip_address(ip_str)

                        # FILTRE : On n'ajoute l'IP que si elle n'est PAS privée ni locale
                        # is_private couvre : 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
                        # is_loopback couvre : 127.0.0.1
                        if not (ip_obj.is_private or ip_obj.is_loopback):
                            all_ips.append(ip_str)

                    except ValueError:
                        # Au cas où l'extraction regex donne quelque chose d'invalide
                        continue

        if not all_ips:
            print("Aucune adresse IP publique trouvée dans les logs.")
            return

        # --- STATISTIQUES GLOBALES ---
        total_hits = len(all_ips)
        unique_visitors = len(set(all_ips))

        print("\n" + "="*50)
        print(f"{'RÉSUMÉ DES STATISTIQUES (IP PUBLIQUES)':^50}")
        print("="*50)
        print(f"Total des requêtes filtrées : {total_hits}")
        print(f"Visiteurs uniques           : {unique_visitors}")
        print("-" * 50)

        # --- TOP 50 ET GÉOLOCALISATION ---
        ip_counts = Counter(all_ips).most_common(50)

        print(f"{'IP Address':<15} | {'Hits':<5} | {'Location':<20}")
        print("-" * 55)

        for ip, count in ip_counts:
            try:
                # Appel API avec timeout de 5 secondes
                response = requests.get(f"{API_URL}{ip}?fields=status,country,city", timeout=5).json()
                if response.get('status') == 'success':
                    location = f"{response.get('city')}, {response.get('country')}"
                else:
                    location = "Unknown (Public)"
            except Exception:
                location = "API Error"

            print(f"{ip:<15} | {count:<5} | {location:<20}")

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{LOG_FILE}' est introuvable.")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    analyze_logs()
