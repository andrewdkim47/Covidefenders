import json
import unittest
import os
import requests
import sqlite3

def write_cache(CACHE_FNAME,country_list):
    with open(CACHE_FNAME, 'w') as outfile:
        json.dump(country_list, outfile)

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

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ db_name)
    cur = conn.cursor()
    return cur, conn

# TODO:
def create_db():
    countries = read_cache(CACHE_COVID)
    cur, conn = setUpDatabase("db.db")

    setUpCountries(countries, cur, conn)

# -------------------- COVID API FUNCTIONS --------------

COVID_COUNTRIES = "https://api.covid19api.com/countries"
dir_path = os.path.dirname(os.path.realpath(__file__))
CACHE_COVID = dir_path + '/' + "cache_countries.json"

def get_country_url(country):
    url = "https://api.covid19api.com/live/country/" + country + "/status/confirmed"
    return url

def create_countries():
    try:
        r = requests.get(COVID_COUNTRIES)
        dict = json.loads(r.text)
    except:
        print("TROUBLE READING COVID_COUNTRIES")
        return None
    all_country_data = []
    for country_dict in dict:
        print(country_dict['Country'])
        country_url = get_country_url(country_dict['Country'])
        try:
            r2 = requests.get(country_url)
            temp = json.loads(r2.text)
            print(temp)
        except:
            print("EXCEPTION WHEN GETTING COUNTRY_URL")
            return None
        if temp:
            all_country_data.append(temp[0])
    write_cache(CACHE_COVID, all_country_data)

# FIXME: get 20 at a time
def setUpCountries(countries, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS countries (name TEXT PRIMARY KEY, countrycode TEXT, locationid TEXT, confirmed INTEGER, deaths INTEGER, recovered INTEGER, active INTEGER)")
    for c in countries:
        cur.execute("INSERT OR IGNORE INTO countries (name, countrycode, locationid, confirmed, deaths, recovered, active) \
            VALUES (?,?,?,?,?,?,?)", (c["Country"], c['CountryCode'], c['LocationID'], c['Confirmed'], c['Deaths'], c['Recovered'], c['Active']))
    conn.commit()

# ---------------- STOCKS API FUNCTIONS -----------------



def main():
    # Create json file
    # create_countries() ONLY RUN THIS IF WE DONT HAVE CACHE_COUNTRIES

    create_db()


if __name__ == "__main__":
    main()