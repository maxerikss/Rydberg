#!/usr/bin/env python3
import sys,os
import requests
import pandas as pd
from typing import *
from simple_term_menu import TerminalMenu

# ==================================================================
# ------------------------- Constants ------------------------------
# ==================================================================

beerTypes = ["Beer", "Lager", "Weissbier", "Ale", "Pale Ale", "Belgian Ale", "Porter", "Stout", "Sour Beer", "Spiced Beer"]
inventoryCategories = ["Beer", "Pale Ale", "Ale", "Belgian Ale", "Stout", "Porter", "Lager", "Sour Beer", "Weissbier", "Spiced Beer", "Cider", "Mixed Drink" ,"Wine"]

# ==================================================================
# ----------------------- Reading API ------------------------------
# ==================================================================

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

# ==================================================================
# ----------------------- Class Definitions-------------------------
# ==================================================================

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

    def printLatex(self, type, out):
        if type in ["beer", "wine"]:
            string = r"\beernew{" + self.name + "}{" + self.category + "}{" + str(self.price) + "}\n"
        elif type == "cider":
            string = r"\beer{" + self.name + "}{" + str(self.price) + "}\n"
        print(string, file=out)



class ProductList:
    def __init__(self):
        self.products: List[Product] = []

    def _printTypes(self, type, productList: List[Product], out, weekly="", standardList=[], regular=False):
            if regular:
                for style in beerTypes:
                    for beer in productList:
                        if beer.category == style and beer.name != weekly and beer.uuid in standardList and int(beer.balance) > 0:
                            beer.printLatex(type, out)
            else:
                for style in beerTypes:
                    for beer in productList:
                        if beer.category == style and beer.name != weekly and beer.uuid not in standardList and int(beer.balance) > 0:
                            beer.printLatex(type, out)

    def add(self, newProduct):
        self.products.append(newProduct)
    
    def addInventory(self, productData, stockData):
        for i in productData:
            newProduct = Product(
                i.get("uuid"),
                i.get("name"),
                i.get("category").get("name"),
                int(i.get('variants')[0].get("price").get("amount")/100),
                "--"
            )
        
            for j in stockData:
                uuid = j.get("productUuid")
                balance = j.get("balance")
                if newProduct.uuid == uuid and newProduct.category in inventoryCategories:
                    newProduct.balance = balance

            self.products.append(newProduct)

        self.products.sort(key=lambda product: product.name)

    def printLatex(self, type, out):
        if type == "beer":
            print(r"\begin{beerSection}{Beer}{Style}{Price}" + "\n", file=out)
            
            beers = [product for product in self.products if product.category in beerTypes]
            # :::::::::::::::::::::::::::
            # .Printing Beer of the Week.
            # :::::::::::::::::::::::::::
            print(r"\specialBeer{Beer of the Week}", file=out)

            print(r"What should be the beer of the week?")
            names = [beer.name for beer in beers if int(beer.balance) > 0]
            beerMenu = TerminalMenu(names)
            beerOfTheWeek = names[beerMenu.show()] 
            for i in self.products:
                if i.name == beerOfTheWeek:
                    i.printLatex(type, out)
            
            # :::::::::::::::::::::::::::
            # ....Reading Regular Beer...
            # :::::::::::::::::::::::::::
            standardBeer = []
            with open("beer.standard", "r") as standard:
                for line in standard:
                    standardBeer.append(line.strip())

                # :::::::::::::::::::::::::::
                # ...Printing Regular Beer...
                # :::::::::::::::::::::::::::
                print(r"\specialBeer{Regular Beer}", file=out)
                self._printTypes(type, beers, out, weekly=beerOfTheWeek, standardList=standardBeer, regular=True)
                
                # :::::::::::::::::::::::::::
                # ...Printing Guesting Beer..
                # :::::::::::::::::::::::::::
                print(r"\specialBeer{Guesting Beer}", file=out)
                self._printTypes(type, beers, out, weekly=beerOfTheWeek, standardList=standardBeer)

            print(r"\end{beerSection}" + "\n", file=out)

                    
        elif type == "cider":
            print(r"\begin{menuSection}{Cider}" + "\n", file=out)
            
            # :::::::::::::::::::::::::::
            # ......Printing Cider.......
            # :::::::::::::::::::::::::::
            print(r"\specialBeer{Cider}", file=out)
            for i in self.products:
                if i.category in ["Cider"] and int(i.balance) > 0:
                    i.printLatex(type, out)

            # :::::::::::::::::::::::::::
            # ...Printing Mixed Drinks...
            # :::::::::::::::::::::::::::
            print(r"\specialBeer{Mixed Drinks}", file=out)
            for i in self.products:
                if i.category in ["Mixed Drink"] and int(i.balance) > 0:
                    i.printLatex(type, out)

            print(r"\end{menuSection}" + "\n", file=out)


        elif type == "wine":
            print(r"\begin{beerSection}{Wine}{Style}{Price}" + "\n", file=out)
            for i in self.products:
                if i.category in ["Wine"]:
                    i.printLatex(type, out)
            print(r"\end{beerSection}" + "\n", file=out)

                

# ==================================================================
# ----------------------- Main Program -----------------------------
# ==================================================================

products = ProductList()
products.addInventory(productsData, stockData)

if len(sys.argv) > 1:
    if sys.argv[1] == "update":
        print("What should be the standard beer?")
        names = [product.name for product in products.products if product.category in beerTypes]
        standardMenu = TerminalMenu(names, multi_select=True, show_multi_select_hint=True)
        standardBeer = standardMenu.show()
        with open("beer.standard", "w") as out:
            for i in standardBeer:
                for j in products.products:
                    if names[i] == j.name:
                        print(j.uuid, file=out)
else:
    with open("../Menu/Beer.tex", "w") as beer, open("../Menu/Cider.tex", "w") as cider:
        products.printLatex("beer", beer)
        products.printLatex("cider", cider)
