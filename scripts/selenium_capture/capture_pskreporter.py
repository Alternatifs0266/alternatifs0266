from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time
import os
import subprocess
import signal

# --- PARAMÈTRES PSKREPORTER ---
URL = "https://pskreporter.info/pskmap.html#preset&callsign=f4lno&timerange=86400&mapCenter=16.4296,14.6259,2.41"
NOM_FICHIER_COMPLET = "/tmp/pskreporter_capture_full.png"
NOM_FICHIER_ROGNE = "/var/www/html/pskreporter_map_rognee.png" 
TEMPS_ATTENTE_CARTE = 120    # Temps d'attente pour le chargement de la carte et des données.
TEMPS_ATTENTE_DATA = 90      # Attente finale pour la capture

# COORDONNÉES DE ROGNAGE (Gauche, Haut, Droite, Bas)
# Ces coordonnées (approximatives) ciblent généralement la zone centrale de la carte dans une fenêtre 1920x1080.
# Vous pourriez avoir besoin de les ajuster après une première exécution.
#COORDONNEES_ROGNEES = (50, 50, 1870, 950) 
COORDONNEES_ROGNEES = (0, 0, 1920, 885) 


def nettoyer_processus_selenium():
    """
    Tente de tuer les processus ChromeDriver et Chrome en cours d'exécution.
    Ceci est un dernier recours si driver.quit() échoue (essentiel pour crontab).
    """
    print("🧹 Nettoyage forcé des processus 'chrome' et 'chromedriver'...")
    processus_a_tuer = ['chromedriver', 'chrome']
    
    for nom_processus in processus_a_tuer:
        try:
            # Recherche des PIDs (Process IDs)
            pids = subprocess.check_output(['pgrep', '-f', nom_processus]).decode().strip().split('\n')
            pids = [p for p in pids if p]
            
            if pids:
                print(f"   -> Suppression de {len(pids)} instances de {nom_processus}...")
                subprocess.run(['kill', '-9'] + pids, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        except subprocess.CalledProcessError:
            pass
        except Exception as e:
            print(f"   -> Erreur inattendue lors du nettoyage de {nom_processus}: {e}")
            
    print("🧹 Nettoyage terminé.")


def prendre_capture_ecran_pskreporter():
    """
    Capture la page PSKReporter, attend le chargement de la carte, et rogne l'image.
    """
    print(f"Ouverture de {URL}...")
    
    # --- Configuration du Driver ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080") 

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # 1. Aller à la page cible
        driver.get(URL) 
        
        # 2. Attendre le chargement complet de la carte et des données
        print(f"Attente de {TEMPS_ATTENTE_CARTE} secondes pour le chargement de la carte...")
        time.sleep(TEMPS_ATTENTE_CARTE)
        
        # NOTE : PSKReporter n'utilise généralement pas de pop-up de consentement agressives.
        # Si une bannière apparaît, il faudra ajouter ici un clic ou un scroll.

        # 3. Capture et Roggnage
        print(f"Attente finale de {TEMPS_ATTENTE_DATA} secondes pour la capture...")
        time.sleep(TEMPS_ATTENTE_DATA)
        driver.save_screenshot(NOM_FICHIER_COMPLET)
        print(f"✅ Capture d'écran complète sauvegardée ({NOM_FICHIER_COMPLET}).")

        img = Image.open(NOM_FICHIER_COMPLET)
        img_rognee = img.crop(COORDONNEES_ROGNEES)
        img_rognee.save(NOM_FICHIER_ROGNE)
        print(f"✅ Image rognée sauvegardée sous : {NOM_FICHIER_ROGNE}")
        driver.quit()

    except Exception as e:
        print(f"❌ Une erreur s'est produite : {e}")
        if driver and os.path.exists(NOM_FICHIER_COMPLET):
             os.remove(NOM_FICHIER_COMPLET)
        
    finally:
        if driver:
            print("🚨 Exécution de driver.quit() pour fermer le navigateur.")
            try:
                driver.quit() 
            except Exception as e_quit:
                print(f"⚠️ Erreur lors de driver.quit(): {e_quit}.")
                # Appel au mécanisme de secours
                nettoyer_processus_selenium() 

if __name__ == "__main__":
    prendre_capture_ecran_pskreporter()
