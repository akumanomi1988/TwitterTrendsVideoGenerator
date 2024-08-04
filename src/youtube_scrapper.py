from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import configparser

# Leer el archivo de configuración
config = configparser.ConfigParser()
config.read('config.ini')

YOUTUBE_BEARER_TOKEN = config['YOUTUBE']['BEARER_TOKEN']

def upload_to_youtube(video_path, title, description):
    """Sube un video a YouTube usando Selenium con bearer token."""
    driver = webdriver.Chrome()
    driver.get("https://www.youtube.com/upload")

    # Añadir el token de autorización en las cookies
    driver.add_cookie({'name': 'Authorization', 'value': f'Bearer {YOUTUBE_BEARER_TOKEN}'})
    driver.refresh()

    time.sleep(5)

    file_input = driver.find_element_by_xpath('//input[@type="file"]')
    file_input.send_keys(video_path)

    time.sleep(5)

    title_input = driver.find_element_by_xpath('//input[@id="title"]')
    title_input.clear()
    title_input.send_keys(title)

    description_input = driver.find_element_by_xpath('//textarea[@id="description"]')
    description_input.clear()
    description_input.send_keys(description)

    next_button = driver.find_element_by_xpath('//ytcp-button[@id="next-button"]')
    next_button.click()
    time.sleep(2)
    next_button.click()
    time.sleep(2)
    next_button.click()

    publish_button = driver.find_element_by_xpath('//ytcp-button[@id="done-button"]')
    publish_button.click()

    time.sleep(5)
    driver.quit()
