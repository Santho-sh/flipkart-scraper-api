import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style
import re
import math
from typing import Union
from fastapi import FastAPI
import mysql.connector
# import schedule
# import time


app = FastAPI()

mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="server",
        database="flipkart"
    )
db = mydb.cursor()

# to run : "uvicorn main:app --reload"


@app.get("/get_low")
def item_details(product: str):
    
    if not check_product(product):
        if add_product(product) == "not found":
            return "product not found"
    
    db.execute("SELECT * FROM table2 where product = (%s)", (product,))
    details = db.fetchall()
    mydb.close()
    return details
    

@app.get("/get_all")
def item_details(product: str):
    if not check_product(product):
        if add_product(product) == "not found":
            return "product not found"
        
    db.execute("SELECT product, link, price FROM table1 where product = (%s)", (product,))
    details = db.fetchall()
    mydb.close()
    return details


    
def check_product(product):
    db.execute("SELECT product FROM table3 WHERE product=(%s)", (product,))
    match = db.fetchall()
    if len(match) == 0:
        return False
    return True

def add_product(product):
    
    url = f"https://www.flipkart.com/search?q={product.lower()}&otracker=AS_Query_HistoryAutoSuggest_2_0&otracker1=AS_Query_HistoryAutoSuggest_2_0&marketplace=FLIPKART"

    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html5lib')

    all_name = soup.find_all("div", attrs={"class": "_4rR01T"})
    all_price = soup.find_all("div", attrs={"class": "_30jeq3"})
    all_links = soup.find_all("a", attrs={"class": "_1fQZEK"})
    all_ratings = soup.find_all("div", attrs={"class": "_3LWZlK"})

    lowest_price = math.inf
    low_link = ""
    rating = 0

    for i in range(len(all_name)):

        if match := re.search(r"(.+) \(.+", all_name[i].text, re.IGNORECASE):

            name = match.group(1).lower()
            rating = all_ratings[i].text

            if name == product.lower():

                price = all_price[i].text
                # remove Rs, commas from price
                price = int(price[1:].replace(",", ""))
                link = all_links[i]["href"]
                link = f"https://www.flipkart.com{link}"

                link_full = re.search(r"(.+)\?.+", link, re.IGNORECASE)
                link = link_full.group(1)

                if price < lowest_price:
                    lowest_price = price
                    low_link = link

                db.execute(
                    "INSERT into table1 (product, link, price) VALUES (%s,%s,%s)", (name, link, price))

    if lowest_price != math.inf:
        db.execute("INSERT into table2 (product, lowest_price, rating, link) VALUES (%s, %s, %s, %s)",
                    (product, lowest_price, rating, low_link))
        db.execute("INSERT into table3 (product, search_link) VALUES (%s, %s)",(product, url))
        mydb.commit()
        return "added"

    return "not found"

# def update_details():
#     db.execute("SELECT product FROM table3")
#     ...

if __name__ == "__main__":
    app()
