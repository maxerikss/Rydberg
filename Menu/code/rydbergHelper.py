import sys,os
import requests
import pandas as pd

# +------------------------+
# |   ###    ########  ####|
# |  ## ##   ##     ##  ## |
# | ##   ##  ##     ##  ## |
# |##     ## ########   ## |
# |######### ##         ## |
# |##     ## ##         ## |
# |##     ## ##        ####|
# +------------------------+

client_ID = "02e805b7-77ee-11ef-b441-6d6e84e75559"
API_key = "eyJraWQiOiIwIiwidHlwIjoiSldUIiwiYWxnIjoiUlMyNTYifQ.eyJpc3MiOiJpWmV0dGxlIiwiYXVkIjoiQVBJIiwiZXhwIjoyNjczNjEyNzM2LCJzdWIiOiJlNGJiZDM5MC1jYmEwLTExZTctYTlhYS1jOWQ4ZmYzZDk3MWQiLCJpYXQiOjE3MjY5MDQ5NjAsImNsaWVudF9pZCI6IjAyZTgwNWI3LTc3ZWUtMTFlZi1iNDQxLTZkNmU4NGU3NTU1OSIsInR5cGUiOiJ1c2VyLWFzc2VydGlvbiIsInVzZXIiOnsidXNlclR5cGUiOiJVU0VSIiwidXVpZCI6ImU0YmJkMzkwLWNiYTAtMTFlNy1hOWFhLWM5ZDhmZjNkOTcxZCIsIm9yZ1V1aWQiOiJlNGJhNzQwMC1jYmEwLTExZTctOGJmYi1lMjA3NzRhZWEwZjUiLCJ1c2VyUm9sZSI6Ik9XTkVSIn0sInNjb3BlIjpbIlJFQUQ6UFJPRFVDVCJdfQ.ITx5w9cuNr7CeCrR4mZGD5XTITWy201VQoiiTUQ_q5rR9wDkBTnoP1mWqP76TGgbgwrRsvFXAyyues2FMhbhAuuZF3pFJoKOt5fwWB2b1xJ8Z2iPSOq33WnONDiwNtvLCwK152FxhDYWL4SFo2bjtG_bOyMrN4d4g5dJlyazR9WSohk1kYGkgVavpe96RaIzW3LPM4MQhFfz7oHqAfUkOiMKYx6GB7jQikaFIvgZHm4G3NmY_AsBGLM48ZNz2PoJa6j9mSYOgwrqKfUvOHpyRqHHIS1uoSEFfCq6KdKAVcpYfFh7qKMkXkobFtd7Wnfaa5BMHgx17dA8mG4nTtKiTg"

postUrl = "https://oauth.zettle.com/token"

postHeaders = {
    "Content-Type": "application/x-www-form-urlencoded"
}

postData = {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "client_id": f"{client_ID}",
    "assertion": f"{API_key}"     
}

access = requests.post(postUrl, headers=postHeaders, data=postData)

accessData = access.json()
bearerToken = accessData.get("access_token")


libraryUrl = "https://products.izettle.com/organizations/self/library"
stockUrl = "https://inventory.izettle.com/v3/stock"
getHeaders = {
    "Authorization": f"Bearer {bearerToken}",  
}

libraryResponse = requests.get(libraryUrl, headers=getHeaders)

allPages = False
stockResponse = []
stockResponse.append(requests.get(stockUrl, headers=getHeaders))
while not allPages:
    linkHeader = stockResponse[-1].headers.get("Link")
    if linkHeader == None:
        allPages = True
    else:
        links = linkHeader.split(", ")
        nextUrl = None
        for link in links:
            url, rel = link.split("; ")
            if 'rel="next"' in rel:
                nextUrl = url.strip("<>")
        stockResponse.append(requests.get(nextUrl, headers=getHeaders))

# Data of the products and the inventory balance
productsData = libraryResponse.json().get("products")
stockData = []
for i in stockResponse:
    stockData.extend(i.json())

# +---------------------------------------------+
# | ######  ##          ###     ######   ###### |
# |##    ## ##         ## ##   ##    ## ##    ##|
# |##       ##        ##   ##  ##       ##      |
# |##       ##       ##     ##  ######   ###### |
# |##       ##       #########       ##       ##|
# |##    ## ##       ##     ## ##    ## ##    ##|
# | ######  ######## ##     ##  ######   ###### |
# +---------------------------------------------+

class Product:
    def __init__(self, uuid, name, category, price, balance):
        self.uuid = uuid
        self.name = name
        self.category = category
        self.price = price
        self.balance = balance
    
    def print(self):
        print(f"UUID: {self.uuid}")
        print(f"Name: {self.name}")
        print(f"Category: {self.category}")
        print(f"Price: {self.price}")
        print(f"Balance: {self.balance}")

listProducts = []


for i in productsData:
    listProducts.append(Product(
        i.get("uuid"),
        i.get("name"),
        i.get("category").get("name"),
        i.get('variants')[0].get("price").get("amount")/100,
        "--"
        )
    )

for i in stockData:
    uuid = i.get("productUuid")
    balance = i.get("balance")
    for j in listProducts:
        if j.uuid == uuid and j.category in ["Beer", "Cider", "Wine"]:
            j.balance = balance
        

for i in listProducts:
    print("--------------------------")
    i.print()
