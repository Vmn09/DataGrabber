from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import time
from nicegui import ui, native
import threading
import asyncio

driver = None

df = pd.DataFrame()
baseURL = None
IDlist = None

isNeededDescription = True
isNeededDimensions = True

mfr_selected = None

description = []
length = []
width = []
height = []
weight = []


#COOKIE KEZELŐ
def cookieHandlerByXPath(XPath):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, XPath))).click()
        print("Cookie popup found")
    except (TimeoutException, NoSuchElementException):
        print("Cookie popup not found")
    time.sleep(2)


#ELEM BETÖLTÉS TIMER
def waitForElementByClassName(toWait):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, toWait)))
    except (TimeoutException, NoSuchElementException):
        print("Element not found")
def waitForElementByXPath(toWait):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, toWait)))
    except (TimeoutException, NoSuchElementException):
        print("Element not found")
def waitForElementByID(toWait):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, toWait)))
    except (TimeoutException, NoSuchElementException):
        print("Element not found")
def waitForElementByName(toWait):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, toWait)))
    except (TimeoutException, NoSuchElementException):
        print("Element not found")


#SZÖVEGEK
def getTextByName(value):
    waitForElementByName(value)
    # WEIDMUELLER ELTÉRŐ MEGNEVEZÉSEI MIATT KELL A TRY-EXCEPT
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
    waitForElementByClassName(value)
    element = driver.find_element(By.CLASS_NAME, value)
    ActionChains(driver)\
        .scroll_to_element(element)\
        .perform()
    text = element.text
    print(f"{value}: {text}")
    return text
def getTextByXPath(value):
    waitForElementByXPath(value)
    element = driver.find_element(By.XPATH, value)
    ActionChains(driver)\
        .scroll_to_element(element)\
        .perform()
    text = element.text
    print(f"{value}: {text}")
    return text


#KATTINTÁS
def clickElementByXPath(toClick):
    waitForElementByXPath(toClick)
    clickable = driver.find_element(By.XPATH, toClick)
    ActionChains(driver)\
        .scroll_to_element(clickable)\
        .perform()
    clickable.click()
def clickElementByClassName(toClick):
    waitForElementByClassName(toClick)
    clickable = driver.find_element(By.CLASS_NAME, toClick)
    ActionChains(driver)\
        .scroll_to_element(clickable)\
        .perform()
    clickable.click()
def clickElementByID(toClick):
    waitForElementByID(toClick)
    clickable = driver.find_element(By.ID, toClick)
    ActionChains(driver)\
        .scroll_to_element(clickable)\
        .perform()
    clickable.click()


#GYÁRTÓ OLDAL ADATOK
def manufacturerSpec(manufacturer):
    specList = {
        "Weidmüller": ["https://catalog.weidmueller.com/catalog/Start.do?ObjectID=", "./ProductIDs/weidmueller.xlsx"],
        "Rittal" : ["https://www.rittal.com/hu-hu/websearch?q=", "./ProductIDs/rittal.xlsx"]
    }
    global baseURL
    baseURL = specList[manufacturer][0]
    global df
    df = pd.read_excel(specList[manufacturer][1])


#GYÁRTÓ FOLYAMATOK
class ManufacturerList:
    def __init__(self):
        self.manufacturers = {
            'Weidmüller': self.weidmueller,
            'Rittal': self.rittal
        }

    def weidmueller(self):
        if isNeededDescription:
            description.append(getTextByName("Verzió"))
        if isNeededDimensions:
            clickElementByID("ui-id-3")
            length.append(getTextByName("Mélység"))
            height.append(getTextByName("Magasság"))
            width.append(getTextByName("Szélesség"))
            weight.append(getTextByName("Nettó tömeg"))

    def rittal(self):
        cookieHandlerByXPath('//*[@id="swal2-html-container"]/div/div/div[2]/div[3]/div/div/button[2]')
        clickElementByClassName("teaser-link")
        time.sleep(5)
        if isNeededDescription:
            getTextByClassName("product-description")
        

async def mainProcess():
    mfr = ManufacturerList()
    while mfr_selected != None:
        manufacturer = mfr_selected
        if manufacturer in mfr.manufacturers:
            manufacturerSpec(manufacturer)
            IDlist = df['cikkszam'].tolist()
            for ID in IDlist:
                driver.get(f"{baseURL}{ID}")
                driver.implicitly_wait(0.5)
                mfr.manufacturers[manufacturer]()
                await asyncio.sleep(5)
        break
    

def dataGrabber():
    global driver
    driver = webdriver.Chrome()
    asyncio.run(mainProcess())
    df['Leírás'] = description
    df['Hosszúság'] = length
    df['Szélesség'] = width
    df['Magasság'] = height
    df['Tömeg'] = width
    timestr = time.strftime('%Y-%m-%d %H-%M')
    df.to_excel(f'./outputs/{mfr_selected} {timestr}.xlsx')
    driver.quit()


def runDataGrabber():
    thread = threading.Thread(target=dataGrabber)
    thread.start()
    startButton.disable()

def webUI():
    mfrDropdown = ManufacturerList()
    mfrDropdown_elements = list(mfrDropdown.manufacturers.keys())
    with ui.card().classes('w-full'):
        with ui.row().classes('justify-between items-center w-full'):
            with ui.row().classes('gap-4'):
                ui.select(mfrDropdown_elements).classes('w-64').bind_value_to(globals(), 'mfr_selected')
                ui.checkbox('Leírás').bind_value(globals(), 'isNeededDescription')
                ui.checkbox('Adatok').bind_value(globals(), 'isNeededDimensions')
            global startButton
            startButton = ui.button('Start', on_click=runDataGrabber)

    ui.run(native=True, title='DataGrabber', reload=False, port=native.find_open_port())


webUI()