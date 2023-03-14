import sqlite3


def sqlcmd(cmd,db):
    ret = []
    CONNEC = sqlite3.connect(db)

    CURS = CONNEC.cursor()
    CURS.execute(cmd)
    rows = CURS.fetchall()
    for row in rows:
        if row == None:
            pass
        else:
            ret.append(row)
    CONNEC.commit()
    CONNEC.close()
    return ret
