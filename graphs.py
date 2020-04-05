import matplotlib
import matplotlib.pyplot as plt
import json
import os

def setup_db():
    #create the connection and cursor
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path +'/'+'db.db')
    cur = conn.cursor()
    return cur, conn

def calculate_covid_date() {

}


def main():
    cur, conn = setup_db()
    
    # Get the figure
    fig = plt.figure()

    # Create bar graph: Country to infected/death ratio

    # Create bar graph: country to infected/recovered ratio.

    # Create Bar Line graph: X: time global affected percentages over time, and zoom stocks over time

    # Create Bar Line graph: X: time global affected percentages over time, and zoom stocks over time

    # Save the figure/
    fig.savefig("covidefenders_graph.png")
    plt.show()

if __name__ == "__main__":
    main()