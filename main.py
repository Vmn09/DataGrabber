from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time

driver = webdriver.Chrome()

df = pd.read_excel("./ProductIDs/weidmueller.xlsx")

baseURL = "https://catalog.weidmueller.com/catalog/Start.do?ObjectID="
IDlist = df['cikkszam'].tolist()
print(IDlist)

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

def clickElementByID(toClick):
    collapsedData = driver.find_element(By.ID, toClick)
    collapsedData.click()

class ManufacturerList:
    def __init__(self):
        self.manufacturers = {
            'weidmueller': self.weidmueller
        }
    def weidmueller(self):
        if isNeededDescription:
            getTextByName("Rendelési szám")
        if isNeededDimensions:
            clickElementByID("ui-id-3")
            getTextByName("Mélység")
            getTextByName("Magasság")
            getTextByName("Szélesség")
            getTextByName("Nettó tömeg")


def mainProcess():
    manufacturer = None
    mfr = ManufacturerList()
    while manufacturer != 'quit':
        manufacturer = input("Enter a manufacturer, quit to end: ").strip().lower()
        if manufacturer in mfr.manufacturers:
            for ID in IDlist:
                driver.get(f"{baseURL}{ID}")
                driver.implicitly_wait(0.5)
                mfr.manufacturers[manufacturer]()
                time.sleep(5)
    

def setupProcess():
    mainProcess()
    driver.quit()

setupProcess()