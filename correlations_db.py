import pandas as pd
import quandl
import math
import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from graph import build_graph, build_complexgraph
import sqlite3
style.use('ggplot')

quandl.ApiConfig.api_key = 'sdAim9z9ENkxuBap7SAp'

'''
    STATS BUILDER
'''
stats = {}

stats['startActual'] = 0
stats['endActual'] = 0
stats['pctChange'] = 0

stats['startOld'] = 0
stats['endOld'] = 0
stats['pctChangeOld'] = 0

stats['startFollowUp'] = 0
stats['endFollowUp'] = 0
stats['pctchgFollowUp'] = 0


def getStatsActual():
    if stats:
        return stats['startActual'], stats['endActual'], stats['pctChange']
    else:
        return "Error"


def getStatsOld():
    if stats:
        return stats['startOld'], stats['endOld'], stats['pctChangeOld']
    else:
        return "Error"


def getStatsFollowUp():
    if stats:
        return stats['startFollowUp'], stats['endFollowUp'], stats['pctchgFollowUp']
    else:
        return "Error"


n_occ = 0


def getOccurrences():
    global n_occ
    if n_occ >= 0:
        occurences = n_occ
        n_occ = 0
        #print(".-.-.-", occurences, n_occ)
        return occurences

    else:
        return "Error"


def getCorrData(nlookback, ndays, database, i, corr_filter, occ):
    db = sqlite3.connect('Data.db')
    step = ndays

    endActual = 0
    startActual = ndays

    endCorr = startActual + i
    startCorr = endCorr + ndays

    endCorrFollowUp = endCorr - ndays
    startCorrFollowUp = endCorr

    # ACTUAL DATA
    actualData = pd.DataFrame(columns=('Idx', 'Last', 'Date'))

    queryActualData_Idx = []
    queryActualData_Last = []
    queryActualData_Date = []

    cursorActual = db.cursor()
    cursorActual.execute('''SELECT Idx, Last, Date FROM '''+database +
                         ''' WHERE Idx >= ? and Idx < ?''', (endActual, startActual,))
    for row in cursorActual:
        queryActualData_Idx.append(row[0])
        queryActualData_Last.append(row[1])
        queryActualData_Date.append(row[2])

    actualData['Idx'] = queryActualData_Idx
    actualData['Last'] = queryActualData_Last
    actualData['Date'] = queryActualData_Date
    # set Idx as index of the dataframe
    actualData.set_index('Idx', drop=True, inplace=True)
    db.commit()

    # CORRELATED DATA
    correlatedData = pd.DataFrame(columns=('Idx', 'Last', 'Date'))

    queryCorrelatedData_Idx = []
    queryCorrelatedData_Last = []
    queryCorrelatedData_Date = []

    cursorCorr = db.cursor()
    cursorCorr.execute('''SELECT Idx, Last, Date FROM '''+database +
                       ''' WHERE Idx >= ? and Idx < ?''', (endCorr, startCorr,))
    for row in cursorCorr:
        queryCorrelatedData_Idx.append(row[0])
        queryCorrelatedData_Last.append(row[1])
        queryCorrelatedData_Date.append(row[2])

    correlatedData['Idx'] = queryCorrelatedData_Idx
    correlatedData['Last'] = queryCorrelatedData_Last
    correlatedData['Date'] = queryCorrelatedData_Date
    # set Idx as index of the dataframe
    correlatedData.set_index('Idx', drop=True, inplace=True)
    db.commit()

    # FOLLOW-UP CORRELATED DATA
    correlatedDataFollowUp = pd.DataFrame(columns=('Idx', 'Last', 'Date'))

    queryCorrelatedDataFollowUp_Idx = []
    queryCorrelatedDataFollowUp_Last = []
    queryCorrelatedDataFollowUp_Date = []

    cursorCorr = db.cursor()
    cursorCorr.execute('''SELECT Idx, Last, Date FROM '''+database +
                       ''' WHERE Idx >= ? and Idx < ?''', (endCorrFollowUp, startCorrFollowUp,))
    for row in cursorCorr:
        queryCorrelatedDataFollowUp_Idx.append(row[0])
        queryCorrelatedDataFollowUp_Last.append(row[1])
        queryCorrelatedDataFollowUp_Date.append(row[2])

    correlatedDataFollowUp['Idx'] = queryCorrelatedDataFollowUp_Idx
    correlatedDataFollowUp['Last'] = queryCorrelatedDataFollowUp_Last
    correlatedDataFollowUp['Date'] = queryCorrelatedDataFollowUp_Date
    # set Idx as index of the dataframe
    correlatedDataFollowUp.set_index('Idx', drop=True, inplace=True)
    db.commit()

    auxCorrelatedData = correlatedData
    auxCorrelatedData['Idx'] = queryActualData_Idx
    # set Idx as index of the dataframe
    auxCorrelatedData.set_index('Idx', drop=True, inplace=True)

    RauxCorrelatedData = auxCorrelatedData.copy()
    RauxCorrelatedData = RauxCorrelatedData.iloc[::-1]
    RauxCorrelatedData['Idx'] = actualData.index
    # set Idx as index of the dataframe
    RauxCorrelatedData.set_index('Idx', drop=True, inplace=True)

    idx2 = []
    for q in range(ndays, ndays+ndays):
        idx2.append(q)

    auxcorrelatedDataFollowUp = correlatedDataFollowUp
    auxcorrelatedDataFollowUp['Idx'] = idx2  # set new column Idx
    auxcorrelatedDataFollowUp.set_index('Idx', drop=True, inplace=True)

    RauxcorrelatedDataFollowUp = auxcorrelatedDataFollowUp.copy()
    RauxcorrelatedDataFollowUp = RauxcorrelatedDataFollowUp.iloc[::-1]
    RauxcorrelatedDataFollowUp['Idx'] = idx2
    RauxcorrelatedDataFollowUp.set_index('Idx', drop=True, inplace=True)

    RauxcorrelatedDataFollowUp.loc[ndays -
                                   1] = RauxCorrelatedData.loc[ndays-1]
    RauxcorrelatedDataFollowUp.sort_index(inplace=True)

    RauxCorrelatedData['Next'] = RauxcorrelatedDataFollowUp['Last']

    chartData = pd.DataFrame()

    chartData['Idx'] = actualData.index
    chartData['Last'] = actualData['Last']

    chartData['Correlated'] = RauxCorrelatedData['Last']
    #chartData['Correlated Date'] = RauxCorrelatedData['Date']
    chartData['Correlated-Follow Up'] = RauxcorrelatedDataFollowUp['Last']
    #chartData['Correlated-Follow Up Date'] = RauxcorrelatedDataFollowUp['Date']
    # set Idx as index of the dataframe
    chartData.set_index('Idx', drop=True, inplace=True)

    df_corr = chartData.pct_change().corr()  # correlation

    chartData = chartData.iloc[::-1]
    chartData['Idx'] = actualData.index
    # set Idx as index of the dataframe
    chartData.set_index('Idx', drop=True, inplace=True)

    RactualData = actualData.copy()
    RactualData['Correlated'] = RauxCorrelatedData['Last']
    RactualData['Correlated-Follow Up'] = RauxcorrelatedDataFollowUp['Last']
    RactualData = RactualData.iloc[::-1]
    RactualData['Idx2'] = actualData.index
    # set Idx as index of the dataframe
    RactualData.set_index('Idx2', drop=True, inplace=True)

    #print(chartData.head(), actualData.head(), RactualData.head())
    print("=======================", i, "/",
          nlookback, "=======================")

    pctchgActual = (
        (chartData['Last'].iloc[-1] - chartData['Last'].iloc[0])/chartData['Last'].iloc[0])*100.0
    pctchgOld = ((RauxCorrelatedData['Last'].iloc[-1] -
                  RauxCorrelatedData['Last'].iloc[0])/RauxCorrelatedData['Last'].iloc[0])*100.0
    pctchgFollowUp = ((RauxcorrelatedDataFollowUp['Last'].iloc[-1] -
                       RauxcorrelatedDataFollowUp['Last'].iloc[0])/RauxcorrelatedDataFollowUp['Last'].iloc[0])*100.0

    dataStr = '%Y-%m-%d'

    startActualdt = RactualData['Date'].iloc[0]
    endActualdt = RactualData['Date'].iloc[-1]

    auxnewStartActualdt = startActualdt[0:10]
    newStartActualdt = datetime.datetime.strptime(
        auxnewStartActualdt, '%Y-%m-%d').strftime("%b %d %Y")
    #print(datetime_object.strftime("%b %d %Y"))

    auxnewEndActualdt = endActualdt[0:10]
    newEndActualdt = datetime.datetime.strptime(
        auxnewEndActualdt, '%Y-%m-%d').strftime("%b %d %Y")
    #print(datetime_object.strftime("%b %d %Y"))

    startCorrelateddt = RauxCorrelatedData['Date'].iloc[0]
    endCorrelateddt = RauxCorrelatedData['Date'].iloc[-1]

    auxnewstartCorrelateddt = startCorrelateddt[0:10]
    newstartCorrelateddt = datetime.datetime.strptime(
        auxnewstartCorrelateddt, '%Y-%m-%d').strftime("%b %d %Y")
    #print(datetime_object.strftime("%b %d %Y"))

    auxnewSendCorrelateddt = endCorrelateddt[0:10]
    newSendCorrelateddt = datetime.datetime.strptime(
        auxnewSendCorrelateddt, '%Y-%m-%d').strftime("%b %d %Y")
    #print(datetime_object.strftime("%b %d %Y"))

    startFollowUpdt = RauxcorrelatedDataFollowUp['Date'].iloc[0]
    endFollowUpdt = RauxcorrelatedDataFollowUp['Date'].iloc[-1]

    auxnewstartFollowUpdt = startFollowUpdt[0:10]
    newstartFollowUpdt = datetime.datetime.strptime(
        auxnewstartFollowUpdt, '%Y-%m-%d').strftime("%b %d %Y")
    #print(datetime_object.strftime("%b %d %Y"))

    auxnewendFollowUpdt = endFollowUpdt[0:10]
    newendFollowUpdt = datetime.datetime.strptime(
        auxnewendFollowUpdt, '%Y-%m-%d').strftime("%b %d %Y")
    #print(datetime_object.strftime("%b %d %Y"))

    print("To predict: ", newStartActualdt,
          newEndActualdt, "%Chg", round(pctchgActual, 2))
    print("Correlated: ", newstartCorrelateddt,
          newSendCorrelateddt, "%Chg", round(pctchgOld, 2))
    print("Follow Up: ", newstartFollowUpdt,
          newendFollowUpdt, "%Chg", round(pctchgFollowUp, 2))
    print("Corr --> ", df_corr['Last']['Correlated'])

    fig, ax1 = plt.subplots()
    ax1.plot(RauxCorrelatedData['Last'], 'b-', label='Correlated')

    followup_c = 'r-'

    if pctchgFollowUp > 0.0:
        followup_c = 'g-'
    elif pctchgFollowUp < 0.0:
        followup_c = 'r-'
    else:
        followup_c = 'b-'

    ax1.plot(
        RauxcorrelatedDataFollowUp['Last'], followup_c, label='Follow-up')
    ax1.yaxis.set_label_position("left")
    ax1.set_ylabel('Correlated and Follow Up')
    ax1.set_xlabel('N days')
    ax1.grid(False)

    ax2 = ax1.twinx()
    ax2.plot(chartData['Last'], 'k--', label='Current')
    ax2.yaxis.set_label_position("right")
    ax2.set_ylabel('Current')
    ax2.grid(False)
    axx = plt.gca()
    fig.legend(bbox_to_anchor=(1, 0.25), bbox_transform=axx.transAxes)
    fig.tight_layout()

    plt.title('Correlation {}'.format(
        round(df_corr['Last']['Correlated'], 2)))
    plt.show()

    newGraph = build_complexgraph(chartData['Last'],
                                  RauxCorrelatedData['Last'], RauxcorrelatedDataFollowUp['Last'], pctchgFollowUp, round(df_corr['Last']['Correlated'], 2))

    db.close()
    return newGraph
