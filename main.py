from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time

driver = webdriver.Chrome()

df = None
baseURL = None
IDlist = None

isNeededDescription = True
isNeededDimensions = True


def getTextByName(value):
    try:
        element = driver.find_element(By.NAME, value)
    except:
        if value == "Mélység":
            alt_value = "Hossz"
        elif value == "Hossz":
            alt_value = "Mélység"
        else:
            raise
        try:
            element = driver.find_element(By.NAME, alt_value)
        except NoSuchElementException:
            raise NoSuchElementException (f"Element not found with names: {value} or {alt_value}")
    ActionChains(driver)\
        .scroll_to_element(element)\
        .perform()
    text = element.text
    print(f"{value}: {text}")
    return text
def getTextByClassName(value):
    element = driver.find_element(By.CLASS_NAME, value)
    ActionChains(driver)\
        .scroll_to_element(element)\
        .perform()
    text = element.text
    print(f"{value}: {text}")
    return text


def clickElementByXPath(toClick):
    clickable = driver.find_element(By.XPATH, toClick)
    ActionChains(driver)\
        .scroll_to_element(clickable)\
        .perform()
    clickable.click()
def clickElementByClassName(toClick):
    clickable = driver.find_element(By.CLASS_NAME, toClick)
    ActionChains(driver)\
        .scroll_to_element(clickable)\
        .perform()
    clickable.click()
def clickElementByID(toClick):
    clickable = driver.find_element(By.ID, toClick)
    ActionChains(driver)\
        .scroll_to_element(clickable)\
        .perform()
    clickable.click()


def manufacturerSpec(manufacturer):
    specList = {
        "weidmueller": ["https://catalog.weidmueller.com/catalog/Start.do?ObjectID=", "./ProductIDs/weidmueller.xlsx"],
        "rittal" : ["https://www.rittal.com/hu-hu/websearch?q=", "./ProductIDs/rittal.xlsx"]
    }
    global baseURL
    baseURL = specList[manufacturer][0]
    global df
    df = pd.read_excel(specList[manufacturer][1])

class ManufacturerList:
    def __init__(self):
        self.manufacturers = {
            'weidmueller': self.weidmueller,
            'rittal': self.rittal
        }
    def weidmueller(self):
        if isNeededDescription:
            getTextByName("Verzió")
        if isNeededDimensions:
            clickElementByID("ui-id-3")
            getTextByName("Mélység")
            getTextByName("Magasság")
            getTextByName("Szélesség")
            getTextByName("Nettó tömeg")

    def rittal(self):
        if driver.find_element(By.XPATH, '//*[@id="swal2-html-container"]/div/div/div[2]/div[3]/div/div/button[2]'):
            clickElementByXPath('//*[@id="swal2-html-container"]/div/div/div[2]/div[3]/div/div/button[2]')
        time.sleep(2)
        clickElementByClassName("teaser-link")
        time.sleep(5)
        if isNeededDescription:
            getTextByClassName("product-description")
        if isNeededDimensions:
            clickElementByID("col_toggle_product_description")




def mainProcess():
    manufacturer = None
    mfr = ManufacturerList()
    while manufacturer != 'quit':
        manufacturer = input("Enter a manufacturer, quit to end: ").strip().lower()
        if manufacturer in mfr.manufacturers:
            manufacturerSpec(manufacturer)
            IDlist = df['cikkszam'].tolist()
            for ID in IDlist:
                driver.get(f"{baseURL}{ID}")
                driver.implicitly_wait(0.5)
                mfr.manufacturers[manufacturer]()
                time.sleep(5)
    

def setupProcess():
    mainProcess()
    driver.quit()

setupProcess()