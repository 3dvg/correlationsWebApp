from flask import Flask, render_template, request, Response
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import io
import base64
from graph import build_graph
from correlations import getCorrData, getLoops, getOccurrences
import time
import math
app = Flask(__name__)

lookback = 600
iterate = 30
step = 30
@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
    ndays = int(request.args.get('ndays'))

    global lookback
    lookback = int(request.args.get('lookback'))

    global step
    step = int(request.args.get('ndays'))

    n_instrument = int(request.args.get('instrument'))
    instrument = ''

    if n_instrument == 1:
        instrument = 'CHRIS/CME_ES1'
    elif n_instrument == 2:
        instrument = 'CHRIS/CME_NQ1'
    elif n_instrument == 3:
        instrument = 'CHRIS/CME_CL1'
    elif n_instrument == 4:
        instrument = 'CHRIS/CME_GC1'
    elif n_instrument == 5:
        instrument = 'CHRIS/CME_US1'

    corr_filter = int(request.args.get('correlation'))

    print(n_instrument, instrument, lookback, corr_filter)
    suggestions_list = []

    for j in range(0, ndays):
        suggestions_list.append(j)

    # graph_list = getCorrData(lookback, ndays, ndays, 'CHRIS/CME_ES1')

    corrData = []
    statistics = {}
    occ = 0
    for i in range(0, lookback, ndays):
        global iterate
        iterate = i

        corrData.append(getCorrData(
            lookback, ndays, instrument, i, corr_filter, occ))

        statistics = getLoops()
        if statistics:
            print(statistics['startActual'],
                  statistics['endActual'], statistics['pctChange'])
        else:
            print("NO HAY STATS")

    occ = getOccurrences()
    return render_template('suggestions.html', nOccurrences=occ, graphs=corrData, instr=instrument, startDate=statistics['startActual'], endDate=statistics['endActual'], pctChange=statistics['pctChange'])


@app.route('/')
def graphs():
    return render_template('graphs.html', iteration=iterate)


@app.route('/progress', methods=['GET', 'POST'])
def progress():
    def generate():
        print(iterate, lookback, step)
        x = 0
        y = 100
        s = int(math.ceil((step - 0)/(lookback-0)*100))
        x = s
        while x < y:
            print(x, y, s)
            time.sleep(3)
            if x > y:
                x = y
            else:
                x = int(math.ceil((iterate - 0)/(lookback-0)*100)) + s
            yield "data:" + str(x) + "\n\n"

            #print('-----> ', x, y, x+s, y-s)
    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0')
