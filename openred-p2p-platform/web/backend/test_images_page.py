#!/usr/bin/env python3
"""
Test de la page /images après correction des erreurs JavaScript
"""

import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

def test_images_page():
    """Test de la page /images"""
    
    print("🧪 Test de la page /images après correction JavaScript")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 1. Test d'accessibilité de base
    print("\n1. 🌐 Test accessibilité page /images...")
    try:
        response = requests.get(f"{base_url}/images", timeout=5)
        if response.status_code == 200:
            print("✅ Page /images accessible")
        else:
            print(f"❌ Page /images retourne {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False
    
    # 2. Test avec browser
    print("\n2. 🖥️ Test JavaScript dans navigateur...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(10)
        
        # Aller sur la page d'images
        driver.get(f"{base_url}/images")
        time.sleep(2)
        
        # Vérifier que la page se charge sans erreur JavaScript
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if js_errors:
            print("❌ Erreurs JavaScript détectées:")
            for error in js_errors:
                print(f"   💥 {error['message']}")
        else:
            print("✅ Aucune erreur JavaScript critique")
        
        # Vérifier la présence des éléments principaux
        print("\n3. 🔍 Vérification éléments interface...")
        
        try:
            # Titre de la page
            title = driver.find_element(By.TAG_NAME, "title").get_attribute("innerHTML")
            print(f"   📄 Titre: {title}")
            
            # Boutons principaux
            buttons = driver.find_elements(By.CLASS_NAME, "btn")
            print(f"   🔘 Boutons trouvés: {len(buttons)}")
            
            # Zone d'upload
            upload_area = driver.find_element(By.ID, "uploadArea")
            if upload_area:
                print("   📤 Zone d'upload présente")
            
            # Sections
            sections = ["myPhantomsSection", "projectionsSection"]
            for section_id in sections:
                try:
                    section = driver.find_element(By.ID, section_id)
                    print(f"   📁 Section {section_id}: Présente")
                except:
                    print(f"   ❌ Section {section_id}: Manquante")
            
        except Exception as e:
            print(f"   ❌ Erreur vérification éléments: {e}")
        
        # Test des fonctions JavaScript
        print("\n4. ⚙️ Test fonctions JavaScript...")
        
        # Tester si loadMyPhantoms est définie
        try:
            result = driver.execute_script("return typeof loadMyPhantoms")
            if result == "function":
                print("   ✅ Fonction loadMyPhantoms: Définie")
            else:
                print(f"   ❌ Fonction loadMyPhantoms: {result}")
        except Exception as e:
            print(f"   ❌ Erreur test loadMyPhantoms: {e}")
        
        # Tester si showActiveStreams est définie
        try:
            result = driver.execute_script("return typeof showActiveStreams")
            if result == "function":
                print("   ✅ Fonction showActiveStreams: Définie")
            else:
                print(f"   ❌ Fonction showActiveStreams: {result}")
        except Exception as e:
            print(f"   ❌ Erreur test showActiveStreams: {e}")
        
        # Tester si connectProjectionServer est définie
        try:
            result = driver.execute_script("return typeof connectProjectionServer")
            if result == "function":
                print("   ✅ Fonction connectProjectionServer: Définie")
            else:
                print(f"   ❌ Fonction connectProjectionServer: {result}")
        except Exception as e:
            print(f"   ❌ Erreur test connectProjectionServer: {e}")
        
        driver.quit()
        
    except Exception as e:
        print(f"❌ Erreur test navigateur: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Test terminé")
    return True

if __name__ == "__main__":
    success = test_images_page()
    sys.exit(0 if success else 1)