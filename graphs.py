import matplotlib
import matplotlib.pyplot as plt
import json
import os
import numpy as np
import sqlite3
from matplotlib.ticker import FormatStrFormatter

dir_path = os.path.dirname(os.path.realpath(__file__))
calculations_path = dir_path + '/' + "calculations.txt"


def setup_db():
    #create the connection and cursor
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path +'/'+'db.db')
    cur = conn.cursor()
    print(len(cur.execute("SELECT * from countries").fetchall()))
    return cur, conn

# (name, countrycode, locationid, confirmed, deaths, recovered, active)
def calculate_covid_date(cur, fig):
    inf_death_ratio = []
    inf_recov_ratio = []
    country_list = []

    calc_death = []
    calc_recov = []

    rows = cur.execute('SELECT name, confirmed, deaths, recovered FROM countries').fetchall()
    for r in rows:
        if r[0] not in country_list:
            country_list.append(r[0])
            d_ratio = float(r[2]) / float(r[1])
            r_ratio = float(r[3]) / float(r[1])
            inf_death_ratio.append(d_ratio)
            inf_recov_ratio.append(r_ratio)
            
            str1 = r[0] + ": " + str(inf_death_ratio[-1])
            str2 = r[0] + ": " + str(inf_recov_ratio[-1])
            calc_death.append(str1)
            calc_recov.append(str2)
            if len(country_list) == 20:
                break

    write_calculations("Covid 1", calc_recov)
    write_calculations("Covid 2", calc_death)

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
    rows = cur.execute('SELECT slack.date, slack.high, slack.low, zoom.high, zoom.low FROM slack JOIN zoom on slack.date = zoom.date').fetchall()
    slack_percents = []
    zoom_percents = []
    dates = []

    slack_calc = []
    zoom_calc = []

    count = 0
    for r in rows:
        dates.append(r[0])
        slack_percents.append((r[1]/float(r[2])))
        s_str = r[0] + " : " + str(slack_percents[-1])
        slack_calc.append(s_str)

        zoom_percents.append((r[3]/float(r[4])))
        z_str = r[0] + " : " + str(zoom_percents[-1])
        zoom_calc.append(z_str)
        count += 1
        if count == 20:
            break

    write_calculations("Zoom", zoom_calc)
    write_calculations("Slack", slack_calc)

    ax1 = fig.add_subplot(1,2,1)
    ax1.plot(dates, slack_percents, 'b-', label="Slack Stock")
    ax1.set_title("Slack Stocks")
    ax1.grid()
    ax1.set_ylim(0.1, 1.5)
    plt.xticks(rotation='vertical')

    ax2 = fig.add_subplot(1,2,2)
    ax2.plot(dates, zoom_percents, 'y-', label="Zoom Stock")
    ax2.set_title("Zoom Stocks")
    ax2.grid()
    ax2.set_ylim(0.1, 1.5)
    plt.xticks(rotation='vertical')

    fig.tight_layout(pad=3.0) # space out subplots

def write_calculations(fromm, file):
    f = open(calculations_path, "a+")
    if fromm == "Zoom":
        f.write("------------------Zoom stock changes over time----------------\n")
    elif fromm == "Slack":
        f.write("----------------Slack Stock Changes Over Time-------------\n")
    elif fromm == "Covid 1":
        f.write("--------------Covid Recovery Rates-----------------\n")
    else:
        f.write("--------------Covid Death Rates-----------------\n")
    for line in file:
            f.write("%s\n" %line)
    f.close()


def main():
    plt.clf()
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