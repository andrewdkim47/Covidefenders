import matplotlib
import matplotlib.pyplot as plt
import json
import os
import numpy as np
import sqlite3

def setup_db():
    #create the connection and cursor
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path +'/'+'db.db')
    cur = conn.cursor()
    return cur, conn

# (name, countrycode, locationid, confirmed, deaths, recovered, active)
def calculate_covid_date(cur, fig):
    inf_death_ratio = []
    inf_recov_ratio = []
    country_list = []

    rows = cur.execute('SELECT name, confirmed, deaths, recovered FROM countries').fetchall()
    for r in rows:
        if r[0] not in country_list:
            country_list.append(r[0])
            d_ratio = float(r[2]) / float(r[1])
            r_ratio = float(r[3]) / float(r[1])
            inf_death_ratio.append(d_ratio)
            inf_recov_ratio.append(r_ratio)
            if len(country_list) == 10:
                break
    y_pos = np.arange(len(country_list))
    plt.bar(y_pos, inf_death_ratio, align='center', alpha=0.5)
    plt.xticks(y_pos, country_list)
    plt.ylabel('Death to Cases ratio')
    plt.title("Death to Cases Ratio for All Countres")
    plt.savefig("covidefenders_graph.png")
    plt.show()
    


def main():
    cur, conn = setup_db()
    
    # Get the figure
    fig = plt.figure()

    # Create bar graph: Country to infected/death ratio
    calculate_covid_date(cur, fig)

    # Create bar graph: country to infected/recovered ratio.

    # Create Bar Line graph: X: time global affected percentages over time, and zoom stocks over time

    # Create Bar Line graph: X: time global affected percentages over time, and zoom stocks over time

    # Save the figure/
    fig.savefig("covidefenders_graph.png")
    plt.show()

if __name__ == "__main__":
    main()