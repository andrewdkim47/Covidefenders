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
    cur.execute("CREATE TABLE IF NOT EXISTS countries (name TEXT PRIMARY KEY, countrycode TEXT, locationid TEXT, confirmed INTEGER, deaths INTEGER, recovered INTEGER, active INTEGER)")
    try:
        r = requests.get(COVID_COUNTRIES)
        dict = json.loads(r.text)
    except:
        print("TROUBLE READING COVID_COUNTRIES")
        return None
    all_country_data = []
    count = 0
    for country_dict in dict:
        # only retrieve 105 countries
        if count == 105:
            break
        country_url = get_country_url(country_dict['Country'])
        try:
            print("getting country url")
            r2 = requests.get(country_url)
            temp = json.loads(r2.text)
        except:
            print("EXCEPTION WHEN GETTING COUNTRY_URL")
            return None
        count += 1
        if temp:
            c = temp[0]
            cur.execute("INSERT OR IGNORE INTO countries (name, countrycode, locationid, confirmed, deaths, recovered, active) \
            VALUES (?,?,?,?,?,?,?)", (c["Country"], c['CountryCode'], c['LocationID'], c['Confirmed'], c['Deaths'], c['Recovered'], c['Active']))
            conn.commit()
            all_country_data.append(temp[0])
        if count % 5 == 0 :
            print('Pausing for a bit...')
            time.sleep(5)
    # Keep backup cache file
    # write_cache(CACHE_COVID, all_country_data)

# ---------------- ALPHAVANTAGE API FUNCTIONS -----------------

ALPHAVANTAGE_KEY = '6XJO8EJY4VV7EE50'
ALPHAVANTAGE_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&apikey=' + ALPHAVANTAGE_KEY + '&symbol='

# creates cache for specified symbol
def create_dpv_cache(symbol):
    try: 
        req = requests.get(ALPHAVANTAGE_URL + symbol)
        dpv = json.loads(req.text)        

    except: 
        print("ERROR: Trouble fetching info for symbol {}".format(symbol))
        return None

    print(dpv['Meta Data']['2. Symbol'])
    cache_name = dir_path + '/' + symbol + '_data.json'
    write_cache(cache_name, dpv)



def main():
    cur, conn = setUpDatabase("db.db")
    create_countries(cur, conn)



if __name__ == "__main__":
    main()