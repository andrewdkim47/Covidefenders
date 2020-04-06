import matplotlib
import matplotlib.pyplot as plt
import json
import os
import numpy as np
import sqlite3
from matplotlib.ticker import FormatStrFormatter

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
            if len(country_list) == 20:
                break
    # Death subplot
    ax1 = fig.add_subplot(1,2,1) # 2x1 grid, first subplot
    ax1.bar(country_list, inf_death_ratio, align='center', alpha=0.5)
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax1.set_title("Death/Cases per Country")
    ax1.set_ylabel("Death/Cases ratio")
    ax1.tick_params(axis='x', which='major', pad=15)
    ax1.grid() # add background lines
    plt.xticks(rotation='vertical')

    # Recovery subplot
    ax2 = fig.add_subplot(122) # 2x1 grid second subplot
    ax2.bar(country_list, inf_recov_ratio, align='center', alpha=0.5)
    ax2.set_title("Recovery/Cases per Country")
    ax2.set_ylabel("Recovery/Cases ratio")
    ax2.tick_params(axis='x', which='major', pad=15)
    ax2.grid()
    plt.xticks(rotation='vertical')

    fig.tight_layout(pad=3.0) # space out subplots

    
# TODO:
def generate_zoom_slack(cur, fig):
    # Need to use JOIN in here
    pass



def main():
    cur, conn = setup_db()
    
    # Get the figure
    fig = plt.figure()

    # Create bar graph: Country to infected/death ratio
    # Create bar graph: country to infected/recovered ratio.
    calculate_covid_date(cur, fig)
    fig.savefig("covid_graph.png")
    plt.show()
    
    plt.clf() # clear plt so we can start fresh
    
    # Create Bar Line graph: X: time global affected percentages over time, and zoom stocks over time
    # Create Bar Line graph: X: time global affected percentages over time, and zoom stocks over time 
    generate_zoom_slack(cur, fig)
    fig.savefig("stocks_graph.png")
    plt.show()

    conn.close()


if __name__ == "__main__":
    main()