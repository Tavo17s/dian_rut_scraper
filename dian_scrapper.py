import re
import time
import pandas as pd
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

url = "https://muisca.dian.gov.co/WebRutMuisca/DefConsultaEstadoRUT.faces"
chrome_path = 'chromedriver.exe'


def chrome_setup():
    chrome_options = ChromeOptions()
    chrome_options.add_argument(
        '--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option(
        'excludeSwitches', ['enable-logging'])

    chrome_service = ChromeService(executable_path=chrome_path)
    return webdriver.Chrome(service=chrome_service, options=chrome_options)


def get_nits():

    df = pd.read_csv('data.csv', sep=',', encoding='utf-8')
    return df['nits'].tolist()


def take_screenshot(browser, idNumber):

    img = Image.open(BytesIO(browser.find_element(
        By.XPATH, '//table[@class="padded-table"]').screenshot_as_png))
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    img.save("pdfs/" + str(idNumber) + '.pdf', "PDF", quality=100)


def send_user_id(browser, idNumber):

    WebDriverWait(browser, 10).until(EC.visibility_of_element_located(
        (By.ID, 'vistaConsultaEstadoRUT:formConsultaEstadoRUT:numNit')))

    browser.find_element(
        By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:numNit").clear()

    browser.find_element(
        By.ID, "vistaConsultaEstadoRUT:formConsultaEstadoRUT:numNit").send_keys(idNumber)

    WebDriverWait(browser, 10).until(EC.element_to_be_clickable(
        (By.ID, 'vistaConsultaEstadoRUT:formConsultaEstadoRUT:btnBuscar'))).click()


def fix_website_values(browser):

    pattern = r'^\?{3}label_(.*?)\?{3}$'
    try:
        WebDriverWait(browser, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'muisca_area')))
    except:
        return

    muisca_table = browser.find_elements(
        By.CLASS_NAME, 'fondoTituloLeftAjustado')

    muisca_table.pop()

    for row in muisca_table:
        old_text = row.text
        cleaned_text = re.sub(pattern, r'\1', old_text)
        browser.execute_script(
            f"arguments[0].innerText = '{cleaned_text}'", row)


def main():

    browser = chrome_setup()
    browser.implicitly_wait(1)
    browser.get(url)
    browser.maximize_window()

    users_data = get_nits()

    for user_data in users_data:
        send_user_id(browser, user_data)

        fix_website_values(browser=browser)

        take_screenshot(browser=browser, idNumber=user_data)

        time.sleep(1)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time
    print(
        f"Execution time of 100 users with multiprocess: {execution_time} seconds")
