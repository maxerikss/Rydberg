#!/usr/bin/env python3
import sys,os
import requests
import pandas as pd
from typing import *
from simple_term_menu import TerminalMenu

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
                if newProduct.uuid == uuid and newProduct.category in ["Beer", "Cider", "Wine"]:
                    newProduct.balance = balance

            self.products.append(newProduct)

        self.products.sort(key=lambda product: product.name)

    def printLatex(self, type, out):
        if type == "beer":
            print(r"\begin{beerSection}{Beer}{Style}{Price}" + "\n", file=out)
            
            # :::::::::::::::::::::::::::
            # .Printing Beer of the Week.
            # :::::::::::::::::::::::::::
            print(r"\specialbeer{Beer of the Week}", file=out)

            print(r"What should be the beer of the week?")
            names = [k.name for k in self.products if k.category in ["Beer"] and int(k.balance) > 0]
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
                print(r"\specialbeer{Regular Beer}", file=out)
                for i in self.products:
                    if i.category in ["Beer"] and i.name != beerOfTheWeek and i.uuid in standardBeer and int(i.balance) > 0:
                        i.printLatex(type, out)
                
                # :::::::::::::::::::::::::::
                # ...Printing Guesting Beer..
                # :::::::::::::::::::::::::::
                print(r"\specialbeer{Guesting Beer}", file=out)
                for i in self.products:
                    if i.category in ["Beer"] and i.name != beerOfTheWeek and i.uuid not in standardBeer and int(i.balance) > 0:
                        i.printLatex(type, out)

                    
        elif type == "cider":
            print(r"\begin{menuSection}{Cider}" + "\n", file=out)
            
            # :::::::::::::::::::::::::::
            # ......Printing Cider.......
            # :::::::::::::::::::::::::::
            print(r"\specialbeero{Cider}", file=out)
            for i in self.products:
                if i.category in ["Cider"] and int(i.balance) > 0:
                    i.printLatex(type, out)

            # :::::::::::::::::::::::::::
            # ...Printing Mixed Drinks...
            # :::::::::::::::::::::::::::
            print(r"\specialbeer{Mixed Drinks}", file=out)
            for i in self.products:
                if i.category in ["Mixed Drinks"] and int(i.balance) > 0:
                    i.printLatex(type, out)


        elif type == "wine":
            print(r"\begin{beerSection}{Wine}{Style}{Price}" + "\n", file=out)
            for i in self.products:
                if i.category in ["Wine"]:
                    i.printLatex(type, out)
                

# ==================================================================
# ----------------------- Main Program -----------------------------
# ==================================================================

products = ProductList()
products.addInventory(productsData, stockData)

if len(sys.argv) > 1:
    if sys.argv[1] == "update":
        print("What should be the standard beer?")
        names = [k.name for k in products.products if k.category in ["Beer"]]
        standardMenu = TerminalMenu(names, multi_select=True, show_multi_select_hint=True)
        standardBeer = standardMenu.show()
        with open("beer.standard", "w") as out:
            for i in standardBeer:
                for j in products.products:
                    if names[i] == j.name:
                        print(j.uuid, file=out)
else:
    with open("beer.tex", "w") as beer, open("cider.tex", "w") as cider, open("wine.tex", "w") as wine:
        products.printLatex("beer", beer)
        products.printLatex("cider", cider)
        #products.printLatex("wine", wine)
