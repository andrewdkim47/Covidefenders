import json
import unittest
import os
import requests

COVID_COUNTRIES = "https://api.covid19api.com/countries"
dir_path = os.path.dirname(os.path.realpath(__file__))
CACHE_FNAME = dir_path + '/' + "cache_countries.json"

def get_country_url(country):
    url = "https://api.covid19api.com/live/country/" + country + "/status/confirmed"
    return url

def write_cache(country_list):
    read_dict = read_cache(CACHE_FNAME)
    with open(CACHE_FNAME, 'w') as outfile:
        json.dump(country_list, outfile)


def create_countries():
    try:
        r = requests.get(COVID_COUNTRIES)
        dict = json.loads(r.text)
    except:
        print("TROUBLE READING COVID_COUNTRIES")
        return None
    all_country_data = []
    for country_dict in dict:
        country_url = get_country_url(country_dict['Country'])
        try:
            r2 = requests.get(country_url)
            temp = json.loads(r2.text)
        except:
            print("EXCEPTION WHEN GETTING COUNTRY_URL")
            return None
        if temp:
            all_country_data.append(temp[0])
    write_cache(all_country_data)
    


def main():
    # Create json file
    create_countries()


if __name__ == "__main__":
    main()