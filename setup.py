import json
import unittest
import os
import requests
import sqlite3
import time

# write a backup jsonified cache file for when api is down
def write_cache(CACHE_FNAME, li):
    with open(CACHE_FNAME, 'w') as outfile:
        json.dump(li, outfile)

# reads CACHE_FNAME and returns a dict from that file
def read_cache(CACHE_FNAME):
    try:
        cache_file = open(CACHE_FNAME, 'r', encoding="utf-8")
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        print("read_cache caused an exception")
        CACHE_DICTION = []
    return CACHE_DICTION

# Setsup sqlite3 database given file output name. Returns the new databases cursor and conn
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ db_name)
    cur = conn.cursor()
    return cur, conn

# -------------------- COVID API FUNCTIONS --------------

COVID_COUNTRIES = "https://api.covid19api.com/countries"
dir_path = os.path.dirname(os.path.realpath(__file__))
CACHE_COVID = dir_path + '/' + "cache_countries.json"

# given country string, returns that countries url
def get_country_url(country):
    url = "https://api.covid19api.com/live/country/" + country + "/status/confirmed"
    return url

# given database cursor and conn, create countries table if not exists and call api for each country and insert corresponding information into the database.
# Pause after every 5, and cap it at 105 entries in the database.
def create_countries(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS countries (name TEXT PRIMARY KEY, countrycode TEXT, confirmed INTEGER, deaths INTEGER, recovered INTEGER, active INTEGER)")
    try:
        r = requests.get(COVID_COUNTRIES)
        dict = json.loads(r.text)
    except:
        print("TROUBLE READING COVID_COUNTRIES")
        return None
    #all_country_data = []
    count = 0
    for country_dict in dict:
        # insert only 20 at a time
        if count == 20:
            break
        found = cur.execute("SELECT name FROM countries WHERE name=?", (country_dict['Country'],)).fetchone()
        if found:
            print("hi")
            continue
        else:
            country_url = get_country_url(country_dict['Country'])
            try:
                r2 = requests.get(country_url)
                temp = json.loads(r2.text)
            except:
                print("EXCEPTION WHEN GETTING COUNTRY_URL")
                return None
            if temp:
                c = temp[0]
                print(temp)
                cur.execute("INSERT OR IGNORE INTO countries (name, countrycode, confirmed, deaths, recovered, active) \
                VALUES (?,?,?,?,?,?)", (c["Country"], c['CountryCode'], c['Confirmed'], c['Deaths'], c['Recovered'], c['Active']))
                print("inserting country")
                count += 1
                conn.commit()
        if count % 5 == 0:
            print('Pausing for a bit...')
            time.sleep(5)
    # Keep backup cache file
    # write_cache(CACHE_COVID, all_country_data)

# ---------------- ALPHAVANTAGE API FUNCTIONS -----------------

ALPHAVANTAGE_KEY = '6XJO8EJY4VV7EE50'
ALPHAVANTAGE_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&apikey=' + ALPHAVANTAGE_KEY + '&symbol='
#ZooM : https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&apikey=6XJO8EJY4VV7EE50&symbol=ZM
#SLACK: https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&apikey=6XJO8EJY4VV7EE50&symbol=WORK


def create_zoom(cur,conn):
    cur.execute("CREATE TABLE IF NOT EXISTS zoom (date TEXT PRIMARY KEY, open REAL, high REAL, low REAL, close REAL, volume REAL)")
    try:
        req = requests.get(ALPHAVANTAGE_URL + "ZM")
        dpv = json.loads(req.text)        
    except: 
        print("ERROR: Trouble fetching info for zoom")
        return None
    count = 0
    for day in dpv['Time Series (Daily)']:
        if count == 20:
            print("inserted 20 for zoom")
            break
        found = cur.execute("SELECT date FROM zoom WHERE date=?", (day,)).fetchone()
        if found:
            print("zoom date already exists!")
            continue
        else:
            cur.execute("INSERT OR IGNORE INTO zoom (date, open, high, low, close, volume) \
                VALUES (?,?,?,?,?,?)", (day, dpv['Time Series (Daily)'][day]['1. open'],
                     dpv['Time Series (Daily)'][day]['2. high'], dpv['Time Series (Daily)'][day]['3. low'], dpv['Time Series (Daily)'][day]['4. close'],
                         dpv['Time Series (Daily)'][day]['5. volume']))
            print("inserting zoom date")
            count += 1
            conn.commit()


def create_slack(cur,conn):
    cur.execute("CREATE TABLE IF NOT EXISTS slack (date TEXT PRIMARY KEY, open REAL, high REAL, low REAL, close REAL, volume REAL)")
    try:
        req = requests.get(ALPHAVANTAGE_URL + "WORK")
        dpv = json.loads(req.text)        
    except: 
        print("ERROR: Trouble fetching info for slack")
        return None
    count = 0
    for day in dpv["Time Series (Daily)"]:
        if count == 20:
            print("inserted 20 for slack")
            break
        found = cur.execute("SELECT date FROM slack WHERE date=?", (day,)).fetchone()
        if found:
            print("slack date already exists!")
            continue
        else:
            cur.execute("INSERT OR IGNORE INTO slack (date, open, high, low, close, volume) \
                VALUES (?,?,?,?,?,?)", (day, dpv['Time Series (Daily)'][day]['1. open'],
                     dpv['Time Series (Daily)'][day]['2. high'], dpv['Time Series (Daily)'][day]['3. low'], dpv['Time Series (Daily)'][day]['4. close'],
                         dpv['Time Series (Daily)'][day]['5. volume']))
            print("inserting slack date")
            count += 1
            conn.commit()

def main():
    cur, conn = setUpDatabase("db.db")
    create_countries(cur, conn)
    print("Done inserting into countries")
    #cur.execute("DROP TABLE IF EXISTS zoom")
    create_zoom(cur, conn)
    print("Done inserting into zoom")

    # 5 calls per minute and 500 calls perday
    print('Pausing for 30 secs...')
    time.sleep(30)
    
    #cur.execute("DROP TABLE IF EXISTS slack")
    create_slack(cur, conn)
    print("Done inserting into slack")
    


if __name__ == "__main__":
    main()