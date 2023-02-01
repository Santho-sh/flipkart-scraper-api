import requests
import json
from bs4 import BeautifulSoup
from colorama import Fore, Style
import re
import math
from typing import Union
from fastapi import FastAPI
import sqlite3


app = FastAPI()

# to run : "uvicorn main:app --reload"

@app.get("/{mobile}")

def item_details(mobile: str):
    conn = sqlite3.connect("flipkart.db")
    db = conn.cursor()
    
    db.execute("SELECT mobile FROM table3 WHERE mobile=(?)", (mobile,))
    db_mobile = db.fetchall()
    
    if len(db_mobile) == 0:
        
        url = f"https://www.flipkart.com/search?q={mobile.lower()}&otracker=AS_Query_HistoryAutoSuggest_2_0&otracker1=AS_Query_HistoryAutoSuggest_2_0&marketplace=FLIPKART"

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

            if match := re.search(r"(.+) \((.+), (.+)\)", all_name[i].text, re.IGNORECASE):

                name = match.group(1).lower()
                color = match.group(2).lower()
                rom = match.group(3)
                rating = all_ratings[i].text
                
                if name == mobile.lower():
                    
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
                        
                    db.execute("INSERT into table1 (mobile, link) VALUES (?, ?)", (name, link))
                    db.execute("INSERT into table2 (price, rom, color) VALUES (?, ?, ?)", (price, rom, color))
                
        if rating != 0:            
            db.execute("INSERT into table3 (mobile, lowest_price, rating, search_link, link) VALUES (?, ?, ?, ?, ?)", (mobile, lowest_price, rating, url, low_link))
            print (f"{mobile} added to database")
        
            db.execute("SELECT * FROM table3 WHERE mobile = (?)", (mobile,))
            details = db.fetchall()
            conn.commit()
            conn.close()
            return details
        
        return "item not found"
    
    else:
        db.execute("SELECT * FROM table3 where mobile = (?)", (mobile,))
        details = db.fetchall()
        conn.close()
        return details 

if __name__ == "__main__":
    app()