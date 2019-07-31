from flask import Flask, render_template, request, Response
#from correlations import getCorrData, getOccurrences, getStatsActual, getStatsFollowUp, getStatsOld
from correlations_db import getCorrData, getOccurrences, getStatsActual, getStatsFollowUp, getStatsOld
import time
import math
from database import create_db, create_df, deletedb, create_dummydb, checkTables, getDB
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    try:
        return render_template("index.html")
    except:
        return render_template('500.html')


@app.route('/app')
def correlations_app():
    try:
        return render_template("app.html")
    except:
        return render_template('500.html')


'''
===============================================
'''
lookback = 0
iterate = 0
step = 0

stop_run = False


def suggestionsAux():
    # create_dummydb()

    # deletedb()

    checkTables()

    create_db()

    checkTables()

    try:
        global stop_run
        stop_run = False
        n_ndays = int(request.args.get('ndays'))
        ndays = 0

        paginationAux = {}

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

        print(n_instrument, getDB(), lookback, corr_filter)
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
                    lookback, ndays, getDB(), i, corr_filter, occ)
                if j == None:
                    print("none")
                    continue
                else:
                    corrData.append(j)
                    # customi = int(i/ndays)
                    # statistics.append(k)
                    statisticsActual.append(getStatsActual())
                    statisticsOld.append(getStatsOld())
                    statisticsFollowUp.append(getStatsFollowUp())
                progress()
                time.sleep(0.01)
        set_stop_run()
        occ = getOccurrences()

        # paginationAux["nOccurrences"] = occ
        paginationAux["graphs"] = corrData
        # paginationAux["instr"] = instrument
        paginationAux["statsActual"] = statisticsActual
        paginationAux["statsOld"] = statisticsOld
        paginationAux["statsFollowUp"] = statisticsFollowUp

        return paginationAux, occ
    except:
        return "ERROR"


@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
    '''try:'''
    data, occ = suggestionsAux()

    charts = data["graphs"]
    actual = data["statsActual"]
    correlated = data["statsOld"]
    followup = data["statsFollowUp"]
    nItems = 6

    charts = [x for x in charts if x != None]
    sCharts = list(dict.fromkeys(charts))
    sCharts = sCharts[:nItems]
    '''for j in sCharts:
        print("___img", j[0:10])'''
    actual = [x for x in actual if x != (0, 0, 0)]
    sActual = actual[:nItems]
    '''for j in sActual:
        print(",,", j)'''
    correlated = [x for x in correlated if x != (0, 0, 0)]
    sCorrelated = list(dict.fromkeys(correlated))
    sCorrelated = sCorrelated[:nItems]
    '''for k in sCorrelated:
        print("--", k)'''
    followup = [x for x in followup if x != (0, 0, 0)]
    sFollowup = list(dict.fromkeys(followup))
    sFollowup = sFollowup[:nItems]
    '''for k in sFollowup:
        print(">>", k)'''

    sdata = {}
    showing = 0

    sdata["graphs"] = sCharts
    sdata["statsActual"] = sActual
    sdata["statsOld"] = sCorrelated
    sdata["statsFollowUp"] = sFollowup
    showing = len(sdata["graphs"])
    '''print(len(sdata["graphs"]), len(sdata["statsActual"]),
          len(sdata["statsOld"]), len(sdata["statsFollowUp"]))'''
    return render_template('suggestions.html', data=sdata, occurrences=occ, showing=showing)
    '''except:
        return render_template('500.html')'''


@app.route("/stop", methods=['GET'])
def set_stop_run():
    try:
        global stop_run
        stop_run = True
        return "Application stopped"
    except:
        return render_template('500.html')


@app.route('/progress', methods=['GET', 'POST'])
def progress():
    try:
        def generate():
            global stop_run
            #print("stopped ==>", stop_run)

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
                # time.sleep(1)
                if x >= y or x+s >= y:
                    # print("JODIDO")
                    x = 100
                else:
                    if lookback == 0:
                        x = 0
                    else:
                        x = int(math.ceil((iterate - 0)/(lookback-0)*100)) + s
                if x >= y:
                    #print("te he pillao jodio")
                    x = 100

                #print('----', x, '----', stop_run)
                yield "data:" + str(x) + "\n\n"

            else:
                return "Progress bar stopped"

        return Response(generate(), mimetype='text/event-stream')
    except:
        return render_template('500.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


'''
===============================================
'''

# create_dummydb()

# deletedb()

# checkTables()

# create_db()

# checkTables()

if __name__ == "__main__":
    app.run(debug=True)
