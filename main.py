import cloudscraper
import random
import telegram_send
import time

from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()
productsNotified = {}

print("Checking if there is stock available in PCC for RTX 3060, 3070, 3080 or 3090")

def scrapThis(urlToScrap):
    resp = scraper.get(urlToScrap)
    soup = BeautifulSoup(resp.content, "html.parser")
    return soup.find_all("div", class_=['disponibilidad-inmediata', 'disponibilidad-moderada', 'disponibilidad-baja'])

def generateData(item):
    product = dict()
    product['link'] = item.parent.parent.find("a")["href"]
    product['name'] = item.parent.parent.find("a")["data-name"]
    product['date'] = round(time.time() * 1000)
    product['notificated'] = False
    return product

def sendNotificationAsshole(product):
    telegram_send.send(messages=[f"There is stock for {product['name']}", f"https://www.pccomponentes.com{product['link']}"])

def isAlreadyNotified(productName):
    global productsNotified
    return productName in productsNotified

def saveProductInMemory(product):
    timeNow = round(time.time() * 1000)
    global productsNotified
    productName = product['name']

    if isAlreadyNotified(productName):
        if timeNow - productsNotified[productName]['date'] > 300000:
            product['date'] = timeNow
            product['notificated'] = False
        else:
            product['notificated'] = True

    productsNotified[productName] = product

while True:
    """BASE_URL = f"https://www.pccomponentes.com/tarjetas-graficas/amd-radeon-rx-550" """
    """ BASE_URL = f"https://www.pccomponentes.com/tarjetas-graficas/geforce-rtx-3060-series/geforce-rtx-3070-series/geforce-rtx-3080-series/geforce-rtx-3090-series/{random.randint(0,9)}" """
    
    items = []
    for i in range(4):
        URL = f"https://www.pccomponentes.com/listado/ajax?idFilters%5B%5D=7793&idFilters%5B%5D=7501&idFilters%5B%5D=7498&idFilters%5B%5D=7504&page={i}&order=relevance&gtmTitle=Tarjetas%20Gr%C3%A1ficas%20GeForce%20RTX%203080%20Series%20GeForce%20RTX%203070%20Series%20GeForce%20RTX%203090%20Series&idFamilies%5B%5D=6"
        if len(items) > 0:
            items.extend(scrapThis(URL))
        else:
            items = scrapThis(f"https://www.pccomponentes.com/tarjetas-graficas/geforce-rtx-3060-series/geforce-rtx-3070-series/geforce-rtx-3080-series/geforce-rtx-3090-series/{random.randint(0,9)}")
            items.extend(scrapThis(URL))

    if len(items) > 0 :
        for item in items:
            itemData = generateData(item)
            saveProductInMemory(itemData)
            
            if productsNotified[itemData['name']]['notificated'] == False:
                print("Product found, proceeding to notificate.")
                sendNotificationAsshole(itemData)
    else :
        print("There is not stock available, relaunching in 5 secs.")

    time.sleep(5)
