from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import time
import os
import subprocess
import signal
from selenium.webdriver.common.by import By 

# --- PARAMÈTRES OPENWEBRX ---
URL = "https://14alt266.freeboxos.fr/openwebrx"
NOM_FICHIER_COMPLET = "/tmp/openwebrx_capture_full.png"
NOM_FICHIER_ROGNE = "/var/www/html/openwebrx_map_rognee.png" 
TEMPS_ATTENTE_PAGE_LOAD = 180 # Temps d'attente spécifié (180 secondes = 3 minutes)
TEMPS_ATTENTE_POST_CLIC = 5 # Attente finale après le clic

# COORDONNÉES DE ROGNAGE (Gauche, Haut, Droite, Bas) - Standard 
# Vous devrez peut-être ajuster ces coordonnées pour cibler la zone spécifique de la cascade.
#COORDONNEES_ROGNEES = (50, 50, 1870, 950) 
COORDONNEES_ROGNEES = (0, 0, 1920, 885) 

# COORDONNÉES DU CLIC CENTRAL
X_CLIC_CENTRE = 960  # (1920 / 2)
Y_CLIC_CENTRE = 540  # (1080 / 2)

# --- FONCTIONS DE BASE ---

def clic_en_pixel(driver, x, y):
    """Simule un clic à une coordonnée (x, y) donnée."""
    actions = ActionChains(driver)
    
    # Déplacer le curseur au coin supérieur gauche (0, 0)
    body = driver.find_element(By.TAG_NAME, "body")
    actions.move_to_element_with_offset(body, 0, 0)
    
    # Déplacer le curseur à la position absolue (X, Y) et cliquer
    actions.move_by_offset(x, y).click().perform()
    
    # Vider la chaîne d'actions
    actions.reset_actions()

def nettoyer_processus_selenium():
    """Tente de tuer les processus ChromeDriver et Chrome en cours d'exécution."""
    print("🧹 Nettoyage forcé des processus 'chrome' et 'chromedriver'...")
    processus_a_tuer = ['chromedriver', 'chrome']
    
    for nom_processus in processus_a_tuer:
        try:
            pids = subprocess.check_output(['pgrep', '-f', nom_processus]).decode().strip().split('\n')
            pids = [p for p in pids if p]
            
            if pids:
                subprocess.run(['kill', '-9'] + pids, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        except subprocess.CalledProcessError:
            pass
        except Exception as e:
            print(f"   -> Erreur inattendue lors du nettoyage de {nom_processus}: {e}")
            
    print("🧹 Nettoyage terminé.")

# --- FONCTION PRINCIPALE ---

def prendre_capture_ecran_openwebrx():
    """
    Capture la page OpenWebRX après une longue attente et un clic central.
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
        
        # 2. Attente prolongée pour le chargement de l'interface et du flux
        print(f"Attente du chargement de la page pendant {TEMPS_ATTENTE_PAGE_LOAD} secondes...")
        time.sleep(TEMPS_ATTENTE_PAGE_LOAD)
        
        # 3. Clic au centre de l'écran (pour fermer les modals/overlays)
        print(f"Tentative de clic au centre de l'écran ({X_CLIC_CENTRE}, {Y_CLIC_CENTRE})...")
        try:
            clic_en_pixel(driver, X_CLIC_CENTRE, Y_CLIC_CENTRE)
            print("   -> Clic central exécuté avec succès. Attente de 1 seconde.")
            time.sleep(1)
        except Exception as e:
            print(f"   -> Erreur lors du clic central: {e}. Continuation.")

        # 4. Capture et Roggnage
        print(f"Attente finale de {TEMPS_ATTENTE_POST_CLIC} secondes pour la capture...")
        time.sleep(TEMPS_ATTENTE_POST_CLIC)
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
                nettoyer_processus_selenium() 

if __name__ == "__main__":
    prendre_capture_ecran_openwebrx()
