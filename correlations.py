import pandas as pd
import quandl
import math
import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from graph import build_graph, build_complexgraph
style.use('ggplot')

quandl.ApiConfig.api_key = 'sdAim9z9ENkxuBap7SAp'

'''
========== DEFS ==========
'''

iterate = 0
stats = {}
n_occ = 0


def getCorrData(lookback, n_days, instrument, i, corr_filter, occ):
    global stats
    global n_occ
    #print("!", occ, n_occ)
    newGraph = None
    # print(i,"/",lookback)
    steptime = datetime.timedelta(days=i)
    deltatime = datetime.timedelta(days=n_days)
    # current data =========================================
    endActual = datetime.datetime.today()  # current end-date
    startActual = endActual - deltatime  # current start-date

    df = quandl.get(instrument, start_date=startActual,
                    end_date=endActual)

    # data to compare =========================================
    # data to compare end-date
    endOld = startActual - datetime.timedelta(days=1) - steptime
    startOld = endOld - deltatime - \
        datetime.timedelta(days=1) - steptime  # data to compare start-date

    vs_data = quandl.get(instrument, start_date=startOld,
                         end_date=endOld)
    vs_data_followup = quandl.get(instrument, start_date=startOld+deltatime,
                                  end_date=endOld+deltatime)

    # print(len(df), len(vs_data), len(vs_data_followup))
    while True:
        if len(df) > len(vs_data):
            n = abs(len(df)-len(vs_data))
            newdelta = datetime.timedelta(days=n)
            startOld = startOld - newdelta
            vs_data = quandl.get(
                instrument, start_date=startOld, end_date=endOld)
            vs_data_followup = quandl.get(instrument, start_date=startOld+deltatime+datetime.timedelta(
                days=1), end_date=endOld+deltatime+datetime.timedelta(days=1))
        elif len(df) < len(vs_data):
            n = abs(len(df)-len(vs_data))
            newdelta = datetime.timedelta(days=n)
            startOld = startOld + newdelta
            vs_data_followup = quandl.get(instrument, start_date=startOld+deltatime+datetime.timedelta(
                days=1), end_date=endOld+deltatime+datetime.timedelta(days=1))
            vs_data = quandl.get(
                instrument, start_date=startOld, end_date=endOld)

        else:
            break

    while True:
        if len(vs_data_followup) > len(vs_data):
            # print("fixing")
            n = abs(len(vs_data_followup)-len(vs_data))
            newdelta = datetime.timedelta(days=n)
            startOld = startOld + newdelta
            vs_data_followup = quandl.get(instrument, start_date=startOld+deltatime+datetime.timedelta(
                days=1), end_date=endOld+deltatime+datetime.timedelta(days=1))

        elif len(vs_data_followup) < len(vs_data):
            # print("fixing")
            n = abs(len(vs_data_followup)-len(vs_data))
            newdelta = datetime.timedelta(days=n)
            startOld = startOld - newdelta
            vs_data_followup = quandl.get(instrument, start_date=startOld+deltatime+datetime.timedelta(
                days=1), end_date=endOld+deltatime+datetime.timedelta(days=1))

        else:
            # print("ok")
            break

    startFollowUp = startOld+deltatime
    endFollowUp = endOld+deltatime

    n_tradingdays = len(df)
    idx = []
    for j in range(0, n_tradingdays):
        idx.append(j)

    idx2 = []
    for q in range(n_tradingdays, n_tradingdays+n_tradingdays):
        idx2.append(q)

    # prepare data
    vs_data = vs_data[['Last']]  # we are only using closing prices
    vs_data['Idx'] = idx  # set new column Idx
    # set Idx as index of the dataframe
    vs_data.set_index('Idx', drop=True, inplace=True)

    # we are only using closing prices
    vs_data_followup = vs_data_followup[['Last']]
    vs_data_followup['Idx'] = idx2  # set new column Idx
    # set Idx as index of the dataframe
    vs_data_followup.set_index('Idx', drop=True, inplace=True)

    # adding a row
    vs_data.loc[len(vs_data)] = vs_data_followup.loc[n_tradingdays]
    vs_data = vs_data.sort_index()  # sorting by index

    '''print(len(df), len(vs_data), len(vs_data_followup))
print(vs_data , vs_data_followup ) '''

    vs_data['Next'] = vs_data_followup['Last']
    # prepare data
    df = df[['Last']]  # we are only using closing prices
    df['Idx'] = idx  # set new column Idx
    # set Idx as index of the dataframe
    df.set_index('Idx', drop=True, inplace=True)
    # add data to compare to the current dataframe
    df['Old'] = vs_data['Last']
    df['FollowUp'] = vs_data['Next']
    df_corr = df.pct_change().corr()  # correlation

    # print(df,vs_data)
    # if df_corr['Last']['Old'] > 0:
    if corr_filter == 1:
        if df_corr['Last']['Old'] > 0.0:
            n_occ = n_occ+1

            startActualdt = datetime.date(
                startActual.year, startActual.month, startActual.day)
            endActualdt = datetime.date(
                endActual.year, endActual.month, endActual.day)

            startOlddt = datetime.date(
                startOld.year, startOld.month, startOld.day)
            endOlddt = datetime.date(endOld.year, endOld.month, endOld.day)

            startFollowUpdt = datetime.date(
                startFollowUp.year, startFollowUp.month, startFollowUp.day)
            endFollowUpdt = datetime.date(
                endFollowUp.year, endFollowUp.month, endFollowUp.day)
            '''print(df_corr)
            print(df['Last'].pct_change(), df['Old'].pct_change())'''
            print("=======================", i, "/",
                  lookback, "=======================")

            pctchgActual = (
                (df['Last'].iloc[-1] - df['Last'].iloc[0])/df['Last'].iloc[0])*100.0
            pctchgOld = (
                (df['Old'].iloc[-1] - df['Old'].iloc[0])/df['Old'].iloc[0])*100.0
            pctchgFollowUp = (
                (vs_data_followup['Last'].iloc[-1] - vs_data_followup['Last'].iloc[0])/vs_data_followup['Last'].iloc[0])*100.0

            '''
                STATS BUILDER
            '''

            stats['startActual'] = '{} - {} - {}'.format(
                startActual.year, startActual.month, startActual.day)
            stats['endActual'] = '{} - {} - {}'.format(
                endActual.year, endActual.month, endActual.day)
            stats['pctChange'] = str(round(pctchgActual, 2))

            stats['startOld'] = '{} - {} - {}'.format(
                startOld.year, startOld.month, startOld.day)
            stats['endOld'] = '{} - {} - {}'.format(
                endOld.year, endOld.month, endOld.day)
            stats['pctChangeOld'] = str(round(pctchgOld, 2))

            stats['startFollowUp'] = '{} - {} - {}'.format(
                startFollowUp.year, startFollowUp.month, startFollowUp.day)
            stats['endFollowUp'] = '{} - {} - {}'.format(
                endFollowUp.year, endFollowUp.month, endFollowUp.day)
            stats['pctchgFollowUp'] = str(round(pctchgFollowUp, 2))

            print("To predict: ", startActualdt, endActualdt,
                  "%Chg", round(pctchgActual, 2), "Period", n_days)
            print("Historical: ", startOlddt, endOlddt, "%Chg",
                  round(pctchgOld, 2), "Period", n_days)
            print("Follow Up: ", startFollowUpdt, endFollowUpdt,
                  "%Chg", round(pctchgFollowUp, 2), "Period", n_days)
            print("Corr --> ", df_corr['Last']['Old'])

            newGraph = build_complexgraph(df['Last'],
                                          vs_data['Last'], vs_data_followup['Last'], pctchgFollowUp, round(df_corr['Last']['Old'], 2))

    elif corr_filter == 2:
        if df_corr['Last']['Old'] > 0.25:
            n_occ = n_occ+1

            startActualdt = datetime.date(
                startActual.year, startActual.month, startActual.day)
            endActualdt = datetime.date(
                endActual.year, endActual.month, endActual.day)

            startOlddt = datetime.date(
                startOld.year, startOld.month, startOld.day)
            endOlddt = datetime.date(endOld.year, endOld.month, endOld.day)

            startFollowUpdt = datetime.date(
                startFollowUp.year, startFollowUp.month, startFollowUp.day)
            endFollowUpdt = datetime.date(
                endFollowUp.year, endFollowUp.month, endFollowUp.day)
            '''print(df_corr)
            print(df['Last'].pct_change(), df['Old'].pct_change())'''
            print("=======================", i, "/",
                  lookback, "=======================")

            pctchgActual = (
                (df['Last'].iloc[-1] - df['Last'].iloc[0])/df['Last'].iloc[0])*100.0
            pctchgOld = (
                (df['Old'].iloc[-1] - df['Old'].iloc[0])/df['Old'].iloc[0])*100.0
            pctchgFollowUp = (
                (vs_data_followup['Last'].iloc[-1] - vs_data_followup['Last'].iloc[0])/vs_data_followup['Last'].iloc[0])*100.0

            '''
                STATS BUILDER
            '''

            stats['startActual'] = '{} - {} - {}'.format(
                startActual.year, startActual.month, startActual.day)
            stats['endActual'] = '{} - {} - {}'.format(
                endActual.year, endActual.month, endActual.day)
            stats['pctChange'] = str(round(pctchgActual, 2))

            stats['startOld'] = '{} - {} - {}'.format(
                startOld.year, startOld.month, startOld.day)
            stats['endOld'] = '{} - {} - {}'.format(
                endOld.year, endOld.month, endOld.day)
            stats['pctChangeOld'] = str(round(pctchgOld, 2))

            stats['startFollowUp'] = '{} - {} - {}'.format(
                startFollowUp.year, startFollowUp.month, startFollowUp.day)
            stats['endFollowUp'] = '{} - {} - {}'.format(
                endFollowUp.year, endFollowUp.month, endFollowUp.day)
            stats['pctchgFollowUp'] = str(round(pctchgFollowUp, 2))

            print("To predict: ", startActualdt, endActualdt,
                  "%Chg", round(pctchgActual, 2), "Period", n_days)
            print("Historical: ", startOlddt, endOlddt, "%Chg",
                  round(pctchgOld, 2), "Period", n_days)
            print("Follow Up: ", startFollowUpdt, endFollowUpdt,
                  "%Chg", round(pctchgFollowUp, 2), "Period", n_days)
            print("Corr --> ", df_corr['Last']['Old'])

            newGraph = build_complexgraph(df['Last'],
                                          vs_data['Last'], vs_data_followup['Last'], pctchgFollowUp, round(df_corr['Last']['Old'], 2))

    elif corr_filter == 3:
        if df_corr['Last']['Old'] > 0.5:
            n_occ = n_occ+1

            startActualdt = datetime.date(
                startActual.year, startActual.month, startActual.day)
            endActualdt = datetime.date(
                endActual.year, endActual.month, endActual.day)

            startOlddt = datetime.date(
                startOld.year, startOld.month, startOld.day)
            endOlddt = datetime.date(endOld.year, endOld.month, endOld.day)

            startFollowUpdt = datetime.date(
                startFollowUp.year, startFollowUp.month, startFollowUp.day)
            endFollowUpdt = datetime.date(
                endFollowUp.year, endFollowUp.month, endFollowUp.day)
            '''print(df_corr)
            print(df['Last'].pct_change(), df['Old'].pct_change())'''
            print("=======================", i, "/",
                  lookback, "=======================")

            pctchgActual = (
                (df['Last'].iloc[-1] - df['Last'].iloc[0])/df['Last'].iloc[0])*100.0
            pctchgOld = (
                (df['Old'].iloc[-1] - df['Old'].iloc[0])/df['Old'].iloc[0])*100.0
            pctchgFollowUp = (
                (vs_data_followup['Last'].iloc[-1] - vs_data_followup['Last'].iloc[0])/vs_data_followup['Last'].iloc[0])*100.0

            '''
                STATS BUILDER
            '''
            stats['startActual'] = '{} - {} - {}'.format(
                startActual.year, startActual.month, startActual.day)
            stats['endActual'] = '{} - {} - {}'.format(
                endActual.year, endActual.month, endActual.day)
            stats['pctChange'] = str(round(pctchgActual, 2))

            stats['startOld'] = '{} - {} - {}'.format(
                startOld.year, startOld.month, startOld.day)
            stats['endOld'] = '{} - {} - {}'.format(
                endOld.year, endOld.month, endOld.day)
            stats['pctChangeOld'] = str(round(pctchgOld, 2))

            stats['startFollowUp'] = '{} - {} - {}'.format(
                startFollowUp.year, startFollowUp.month, startFollowUp.day)
            stats['endFollowUp'] = '{} - {} - {}'.format(
                endFollowUp.year, endFollowUp.month, endFollowUp.day)
            stats['pctchgFollowUp'] = str(round(pctchgFollowUp, 2))

            print("To predict: ", startActualdt, endActualdt,
                  "%Chg", round(pctchgActual, 2), "Period", n_days)
            print("Historical: ", startOlddt, endOlddt, "%Chg",
                  round(pctchgOld, 2), "Period", n_days)
            print("Follow Up: ", startFollowUpdt, endFollowUpdt,
                  "%Chg", round(pctchgFollowUp, 2), "Period", n_days)
            print("Corr --> ", df_corr['Last']['Old'])

            newGraph = build_complexgraph(df['Last'],
                                          vs_data['Last'], vs_data_followup['Last'], pctchgFollowUp, round(df_corr['Last']['Old'], 2))

    else:
        n_occ = n_occ+1

        startActualdt = datetime.date(
            startActual.year, startActual.month, startActual.day)
        endActualdt = datetime.date(
            endActual.year, endActual.month, endActual.day)

        startOlddt = datetime.date(
            startOld.year, startOld.month, startOld.day)
        endOlddt = datetime.date(endOld.year, endOld.month, endOld.day)

        startFollowUpdt = datetime.date(
            startFollowUp.year, startFollowUp.month, startFollowUp.day)
        endFollowUpdt = datetime.date(
            endFollowUp.year, endFollowUp.month, endFollowUp.day)
        '''print(df_corr)
        print(df['Last'].pct_change(), df['Old'].pct_change())'''
        print("=======================", i, "/",
              lookback, "=======================")

        pctchgActual = (
            (df['Last'].iloc[-1] - df['Last'].iloc[0])/df['Last'].iloc[0])*100.0
        pctchgOld = (
            (df['Old'].iloc[-1] - df['Old'].iloc[0])/df['Old'].iloc[0])*100.0
        pctchgFollowUp = (
            (vs_data_followup['Last'].iloc[-1] - vs_data_followup['Last'].iloc[0])/vs_data_followup['Last'].iloc[0])*100.0

        '''
            STATS BUILDER
        '''

        stats['startActual'] = '{} - {} - {}'.format(
            startActual.year, startActual.month, startActual.day)
        stats['endActual'] = '{} - {} - {}'.format(
            endActual.year, endActual.month, endActual.day)
        stats['pctChange'] = str(round(pctchgActual, 2))

        stats['startOld'] = '{} - {} - {}'.format(
            startOld.year, startOld.month, startOld.day)
        stats['endOld'] = '{} - {} - {}'.format(
            endOld.year, endOld.month, endOld.day)
        stats['pctChangeOld'] = str(round(pctchgOld, 2))

        stats['startFollowUp'] = '{} - {} - {}'.format(
            startFollowUp.year, startFollowUp.month, startFollowUp.day)
        stats['endFollowUp'] = '{} - {} - {}'.format(
            endFollowUp.year, endFollowUp.month, endFollowUp.day)
        stats['pctchgFollowUp'] = str(round(pctchgFollowUp, 2))

        print("To predict: ", startActualdt, endActualdt,
              "%Chg", round(pctchgActual, 2), "Period", n_days)
        print("Historical: ", startOlddt, endOlddt, "%Chg",
              round(pctchgOld, 2), "Period", n_days)
        print("Follow Up: ", startFollowUpdt, endFollowUpdt,
              "%Chg", round(pctchgFollowUp, 2), "Period", n_days)
        print("Corr --> ", df_corr['Last']['Old'])

        newGraph = build_complexgraph(df['Last'],
                                      vs_data['Last'], vs_data_followup['Last'], pctchgFollowUp, round(df_corr['Last']['Old'], 2))

    return newGraph, stats


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


def getOccurrences():
    global n_occ
    if n_occ >= 0:
        occurences = n_occ
        n_occ = 0
        #print(".-.-.-", occurences, n_occ)
        return occurences

    else:
        return "Error"


'''
========== MAIN ==========
'''

# user input data
'''n_days = 30  # user input
step = 30
lookback = 90'''
# convert user input into datetime object


instrument = 'CHRIS/CME_ES1'
# loop loopback step
# getCorrData(lookback, n_days, step, instrument)
# print(n_occ)
