import sqlite3
import quandl
import datetime
import pandas as pd

ydayTable_ES = 'ES0'


def create_dummydb():
    global ydayTable_ES
    db = sqlite3.connect('Data.db')
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS "+ydayTable_ES +
                   "(Idx INTEGER PRIMARY KEY, Last FLOAT, Date DATETIME)")

    db.commit()
    db.close()
    print("dummy table created")


def deletedb():
    table_ES = "ES_"+datetime.datetime.today().strftime("%m%d%Y")

    db = sqlite3.connect('Data.db')
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS "+table_ES)
    db.commit()
    db.close()


def create_db():
    db = sqlite3.connect('Data.db')

    max_days = 7300

    deltatime = datetime.timedelta(days=max_days)
    end = datetime.datetime.today()
    start = end - deltatime

    df_ES = quandl.get('CHRIS/CME_ES1', start_date=start, end_date=end)

    df_ES.drop(['Open', 'High', 'Low', 'Previous Day Open Interest',
                'Volume', 'Change', 'Last'], 1, inplace=True)

    df_ES = df_ES.iloc[::-1]

    df_ES = df_ES.rename(columns={"Settle": "Last"})
    n_ES_maxtradingdays = len(df_ES)
    maxidx_ES = []
    for j in range(0, n_ES_maxtradingdays):
        maxidx_ES.append(j)

    df_ES['Idx'] = maxidx_ES  # set new column Idx
    df_ES['Date'] = df_ES.index

    # set Idx as index of the dataframe
    df_ES.set_index('Idx', drop=True, inplace=True)

    table_ES = "ES_"+datetime.datetime.today().strftime("%m%d%Y")
    print(table_ES)

    cursor = db.cursor()

    global ydayTable_ES
    print(ydayTable_ES, table_ES)

    if table_ES != ydayTable_ES:
        cursor.execute("CREATE TABLE IF NOT EXISTS "+table_ES +
                       "(Idx INTEGER PRIMARY KEY, Last FLOAT, Date DATETIME)")

        db.commit()

        cursor.execute("DROP TABLE "+ydayTable_ES)

        for index, row in df_ES.iterrows():
            cursor.execute("INSERT INTO "+table_ES+"(Idx, Last, Date)VALUES(:Idx, :Last, :Date)",
                           {'Idx': index, 'Last': row['Last'], 'Date': row['Date'].strftime('%Y-%m-%d %H-%M-%S')})
        # db.commit()

        ydayTable_ES = table_ES
        print("-- ", ydayTable_ES, table_ES)

        if table_ES != ydayTable_ES:
            print("it doesnt exists")
        else:
            print("exists!!!")

    else:
        print("it already exists... running code")

    db.commit()
    db.close()


def checkTables():
    # show all tables
    db = sqlite3.connect('Data.db')
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Databases --> ", cursor.fetchall())
    # db.close()

    return cursor.fetchall()


def checkData():
    db = sqlite3.connect('Data.db')
    cursor = db.cursor()
    table_ES = "ES_"+datetime.datetime.today().strftime("%m%d%Y")
    cursor.execute("SELECT Idx, Last FROM "+table_ES+" where Idx < 30")
    for row in cursor:
        print(row[0], row[1])
    db.close()


def getDB():
    table_ES = "ES_"+datetime.datetime.today().strftime("%m%d%Y")
    return table_ES


# create_dummydb()

# deletedb()

# checkTables()

# create_db()

# checkData()

# checkTables()


'''if checkTables() == []:
    print("hay", checkTables())
else:
    print("ha--y", checkTables())'''
