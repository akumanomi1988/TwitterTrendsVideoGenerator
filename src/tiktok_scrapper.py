from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import configparser

# Leer el archivo de configuración
config = configparser.ConfigParser()
config.read('config.ini')

TIKTOK_BEARER_TOKEN = config['TIKTOK']['BEARER_TOKEN']

def upload_to_tiktok(video_path, description):
    """Sube un video a TikTok usando Selenium con bearer token."""
    driver = webdriver.Chrome()
    driver.get("https://www.tiktok.com/upload")

    # Añadir el token de autorización en las cookies
    driver.add_cookie({'name': 'Authorization', 'value': f'Bearer {TIKTOK_BEARER_TOKEN}'})
    driver.refresh()

    time.sleep(5)

    file_input = driver.find_element_by_xpath('//input[@type="file"]')
    file_input.send_keys(video_path)

    time.sleep(5)

    description_input = driver.find_element_by_xpath('//textarea[@id="text"]')
    description_input.send_keys(description)

    publish_button = driver.find_element_by_xpath('//button[text()="Post"]')
    publish_button.click()

    time.sleep(5)
    driver.quit()
