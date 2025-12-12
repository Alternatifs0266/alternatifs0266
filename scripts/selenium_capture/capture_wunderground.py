from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import time
import os

URL = "https://www.wunderground.com/dashboard/pws/IVALBO70"
NOM_FICHIER_COMPLET = "/tmp/wunderground_capture_full.png"
NOM_FICHIER_ROGNE = "/var/www/html/wunderground_capture_rognee.png" 
TEMPS_ATTENTE_DATA = 5       
SCROLL_OFFSET_Y = 190
COORDONNEES_ROGNEES = (320, 240, 1270, 840) 
CLICS_SEQUENTIELS = [
    # Clic 1: Consentement des cookies (Original)
    {"x": 1564, "y": 584, "attente_apres": 5, "description": "Consentement Cookies"},
    # Clic 2: Première pop-up
    {"x": 22, "y": -500, "attente_apres": 5, "description": "Ouverture option"},
    # Clic 3: Deuxième pop-up
    {"x": 286, "y": 67, "attente_apres": 5, "description": "Clic Celcius"}
]

def clic_en_pixel(driver, x, y):
    """Simule un clic à une coordonnée (x, y) donnée."""
    # ActionChains permet d'effectuer des actions de souris complexes
    actions = ActionChains(driver)

    # Réinitialiser la position du curseur au coin (0,0) avant le déplacement
    # pour que move_by_offset soit absolu (approximation)
    actions.move_by_offset(0, 0)

    # Effectuer le déplacement et le clic
    # Nous utilisons un déplacement relatif après un reset pour simuler un clic absolu
    actions.move_by_offset(x, y).click().perform()

def prendre_capture_ecran_wunderground():
    """
    Capture la page Wunderground, force les clics séquentiels en pixel, et rogne l'image.
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

        # 1. Aller à la page cible et attendre le chargement initial
        driver.get(URL)
        print("Attente du chargement initial (5 secondes)...")
        time.sleep(5)

        # 2. Exécution des clics séquentiels
        for clic in CLICS_SEQUENTIELS:
            x, y = clic["x"], clic["y"]
            attente = clic["attente_apres"]
            description = clic["description"]

            print(f"Tentative de clic '{description}' aux coordonnées: ({x}, {y})...")

            try:
                clic_en_pixel(driver, x, y)
                print(f"   -> Clic simulé réussi. Attente de {attente} secondes.")
                time.sleep(attente)
            except Exception as e:
                print(f"   -> Erreur lors du clic '{description}': {e}. Continuation.")
                driver.quit()

        # 2. SCROLL VERS LE BAS
        print(f"Défilement de {SCROLL_OFFSET_Y} pixels vers le bas...")
        # L'argument (0, 190) signifie: 0 en X (horizontal), 190 en Y (vertical, vers le bas)
        driver.execute_script(f"window.scrollBy(0, {SCROLL_OFFSET_Y});") 
        time.sleep(1) # Petite pause pour laisser le rendu se faire

        # 3. Capture et Roggnage
        print(f"Attente finale de {TEMPS_ATTENTE_DATA} secondes pour le chargement des données...")
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
            driver.quit()

if __name__ == "__main__":
    prendre_capture_ecran_wunderground()
