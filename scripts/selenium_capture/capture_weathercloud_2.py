from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from PIL import Image # <<< NOUVEAU : Importation de Pillow
import time
import os

# --- PARAMÈTRES ---
URL = "https://app.weathercloud.net/d3643884531#profile"
NOM_FICHIER_COMPLET = "/tmp/weathercloud2_capture_full.png"
NOM_FICHIER_ROGNE = "/var/www/html/weathercloud2_capture_rognee.png" # Nouveau nom de fichier
TEMPS_MAX_ATTENTE_BOUTON = 10 
TEMPS_ATTENTE_DATA = 5       

# >>> COORDONNÉES DE ROGNAGE (Gauche, Haut, Droite, Bas) <<<
# Vous avez demandé : 240, 64px à 1610, 470px
COORDONNEES_ROGNEES = (30, 70, 980, 570) 
# ---------------------------------------------------------

# SÉLECTEUR CIBLÉ POUR LE BOUTON "ACCEPTER" (Basé sur le script précédent)
SELECTEUR_BOUTON_COOKIES = "button.fc-cta-consent" 

def prendre_capture_ecran_et_rogner(url, nom_fichier_complet, nom_fichier_rogne):
    """
    Prend une capture d'écran, gère le clic, et rogne l'image finale.
    """
    print(f"Ouverture de {url}...")
    
    # --- Configuration du Driver ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    #chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--window-size=1024,768")

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # 1. Injection des Cookies
        driver.get("https://app.weathercloud.net/") 
        driver.add_cookie({'name': 'WeathercloudCookieAgreed', 'value': 'true', 'domain': 'app.weathercloud.net', 'path': '/'})
        driver.add_cookie({'name': 'WeathercloudTrialPopup', 'value': '1', 'domain': 'app.weathercloud.net', 'path': '/'})
        
        # 2. Aller à la page cible et Clic
        driver.get(url) 
        
        try:
            bouton = WebDriverWait(driver, TEMPS_MAX_ATTENTE_BOUTON).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTEUR_BOUTON_COOKIES))
            )
            bouton.click()
            print("   -> Clic simulé sur le bouton de consentement.")
            time.sleep(1) 
        except TimeoutException:
            print("   -> Bouton de consentement non trouvé à temps. Continuation.")
            driver.quit()

        # 3. Capture de l'écran complet
        print(f"Attente de {TEMPS_ATTENTE_DATA} secondes pour les données...")
        time.sleep(TEMPS_ATTENTE_DATA)
        driver.save_screenshot(nom_fichier_complet)
        print(f"✅ Capture d'écran complète sauvegardée ({nom_fichier_complet}).")

        # 4. Rogner l'image (Pillow)
        img = Image.open(nom_fichier_complet)
        
        # Le format de crop est (left, upper, right, lower)
        # 240, 64 sont les coordonnées du coin supérieur gauche.
        # 1610, 470 sont les coordonnées du coin inférieur droit.
        img_rognee = img.crop(COORDONNEES_ROGNEES)
        
        img_rognee.save(nom_fichier_rogne)
        print(f"✅ Image rognée sauvegardée sous : {nom_fichier_rogne}")
        driver.quit()

    except Exception as e:
        print(f"❌ Une erreur s'est produite : {e}")
        # Tenter de nettoyer le fichier complet si le rognage a échoué
        if os.path.exists(nom_fichier_complet):
             os.remove(nom_fichier_complet)
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    prendre_capture_ecran_et_rogner(URL, NOM_FICHIER_COMPLET, NOM_FICHIER_ROGNE)
