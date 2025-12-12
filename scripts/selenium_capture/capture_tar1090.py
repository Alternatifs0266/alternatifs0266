from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import subprocess
import signal

# --- PARAMÈTRES ADS-B EXCHANGE SIMPLIFIÉS ---
URL = "https://14alt266.freeboxos.fr/adsbx/"
NOM_FICHIER_COMPLET = "/var/www/html/adsbx_capture_complete.png"
TEMPS_ATTENTE_PAGE = 30     # Attente spécifiée (30 secondes)
TEMPS_ATTENTE_FINALE = 5    # Petite attente post-chargement/rendu

# --- FONCTION DE NETTOYAGE ---

def nettoyer_processus_selenium():
    """Tente de tuer les processus ChromeDriver et Chrome en cours d'exécution."""
    print("🧹 Nettoyage forcé des processus 'chrome' et 'chromedriver'...")
    processus_a_tuer = ['chromedriver', 'chrome']
    
    for nom_processus in processus_a_tuer:
        try:
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


# --- FONCTION PRINCIPALE ---

def prendre_capture_ecran_adsbx_simple():
    """
    Ouvre l'URL, attend 30s, et sauvegarde la capture d'écran complète.
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
        
        # 2. Attente de chargement
        print(f"Attente du chargement de la page pendant {TEMPS_ATTENTE_PAGE} secondes...")
        time.sleep(TEMPS_ATTENTE_PAGE)
        
        # 3. Attente finale avant capture
        print(f"Attente finale de {TEMPS_ATTENTE_FINALE} secondes pour la capture...")
        time.sleep(TEMPS_ATTENTE_FINALE)
        
        # 4. Capture
        driver.save_screenshot(NOM_FICHIER_COMPLET)
        print(f"✅ Capture d'écran complète sauvegardée sous : {NOM_FICHIER_COMPLET}")

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
    prendre_capture_ecran_adsbx_simple()
