from flask import Flask, render_template, request, Response
from correlations import getCorrData, getOccurrences, getStatsActual, getStatsFollowUp, getStatsOld
import time
import math
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    return render_template("index.html")


@app.route('/app')
def correlations_app():
    return render_template("app.html")


'''
===============================================
'''
lookback = 0
iterate = 0
step = 0

stop_run = False


@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
    global stop_run
    stop_run = False
    n_ndays = int(request.args.get('ndays'))
    ndays = 0
    if n_ndays == 1:
        ndays = 30
    elif n_ndays == 2:
        ndays = 90
    elif n_ndays == 3:
        ndays = 180
    elif n_ndays == 4:
        ndays = 365

    global lookback
    n_lookback = int(request.args.get('lookback'))
    if n_lookback == 1:
        lookback = 730
    elif n_lookback == 2:
        lookback = 1095
    elif n_lookback == 3:
        lookback = 1825
    elif n_lookback == 4:
        lookback = 2920
    elif n_lookback == 5:
        lookback = 4745

    global step
    step = ndays

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
    '''suggestions_list = []

    for j in range(0, ndays):
        suggestions_list.append(j)'''

    # graph_list = getCorrData(lookback, ndays, ndays, 'CHRIS/CME_ES1')

    corrData = []
    statisticsActual = []
    statisticsOld = []
    statisticsFollowUp = []
    occ = 0
    for i in range(0, lookback, ndays):
        if not stop_run:
            global iterate
            iterate = i

            j = getCorrData(
                lookback, ndays, instrument, i, corr_filter, occ)

            corrData.append(j)
            # customi = int(i/ndays)

            # statistics.append(k)
            statisticsActual.append(getStatsActual())
            statisticsOld.append(getStatsOld())
            statisticsFollowUp.append(getStatsFollowUp())
            progress()
    set_stop_run()
    occ = getOccurrences()
    print(stop_run)
    return render_template('suggestions.html', nOccurrences=occ, graphs=corrData, instr=instrument, statsActual=statisticsActual, statsOld=statisticsOld, statsFollowUp=statisticsFollowUp)


@app.route("/stop", methods=['GET'])
def set_stop_run():
    global stop_run
    stop_run = True
    return "Application stopped"


@app.route('/progress', methods=['GET', 'POST'])
def progress():
    def generate():
        global stop_run
        print("stopped ==>", stop_run)

        if not stop_run:
            # print("-----------------", iterate, "/", lookback, step)
            print("progress bar running... ")
            y = 100
            if lookback == 0:
                s = 0
            else:
                s = int(math.floor((step - 0)/(lookback-0)*100))
            x = s

            # print(x, y, s)
            # time.sleep(3)
            if x >= y or x+s >= y:
                print("JODIDO")
                x = 100
            else:
                if lookback == 0:
                    x = 0
                else:
                    x = int(math.ceil((iterate - 0)/(lookback-0)*100)) + s
            if x >= y:
                print("te he pillao jodio")
                x = 100

            print('----', x, '----', stop_run)
            yield "data:" + str(x) + "\n\n"

        else:
            return "Progress bar stopped"

    return Response(generate(), mimetype='text/event-stream')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


'''
===============================================
'''
if __name__ == "__main__":
    app.run()
