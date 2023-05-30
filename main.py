from flask import Flask, request, redirect, render_template, jsonify, make_response
from bs4 import BeautifulSoup
import requests
import time
import base64
import json
import static.sqlmng as sql3
import static.enclib
import os
import random
import re


#-----Security-----#

FilterRes = {
    "AllowEnglish" : "a-zA-Z", 
    "AllowNumber" : "0-9",
    "AllowKorean" : "ㄱ-ㅎㅏ-ㅣ가-힣", 
    "AllowUnderScoreDot" : "\\_\\.",
    "AllowSpace" : " "
}
URLexpression = "https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)"

def MakeExpression(*options: str):
    return re.compile("[^"+"".join(options)+"]")

#-----SQL-----#

class Sql:
    def __init__(self,table,db='static/DBdpp.db') -> None:
        self.db = db
        self.table = table
        self.data = {}
    def selectFromDB(self, columns="*", where="1"):
        query = "SELECT {} FROM {} WHERE {};".format(columns, self.table, where)
        return sql3.sqlcmd(query, self.db)
    def deleteFromDB(self, where: str):
        query = "DELETE FROM {} WHERE {}".format(self.table, where)
        return sql3.sqlcmd(query, self.db)
    def insertIntoDB(self):
        columns_str = "(" + ", ".join(self.data.keys()) + ")"
        values_str = "(" + ", ".join(["'{}'".format(value) for value in self.data.values()]) + ")"
        query = "INSERT INTO {} {} VALUES {}".format(self.table, columns_str, values_str)
        return sql3.sqlcmd(query, self.db)
    def updateDB(self, where: str):
        set_str = ", ".join(["{}='{}'".format(key, value) for key, value in self.data.items()])
        query = "UPDATE {} SET {} WHERE {};".format(self.table, set_str, where)
        return sql3.sqlcmd(query, self.db)

#-----Server-----#

app = Flask(__name__)

try:
    FLAG = open('./prob/flag.txt', 'r').read()
except:
    FLAG = 'ㅍㅡㄹㄹㅐㄱㅡzz'

'''def refresh_docker(deadtime):
    client = docker.from_env()
    deadtime_delta = datetime.timedelta(hours=deadtime)
    deadtime_delta_seconds = deadtime_delta.total_seconds()
    containers = client.containers.list(all=True)
    if containers:
        for container in containers:
            start_time_str = container.attrs['Created']
            start_time = datetime.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            livetime = (datetime.datetime.utcnow() - start_time).total_seconds()
            if livetime > deadtime_delta_seconds:
                container.stop()
                container.remove()'''

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", hint=0), 200
    elif request.method == "POST":
        if request.form.get("flag") == FLAG:
            return "<script>alert(\"Correct!!\");location.href=\"portf\";</script>", 200
        else:
            return "<script>alert(\"Wrong!!\");history.back(-1);</script>", 200
    return "", 400

@app.route("/hint")
def hint():
    return render_template("index.html", pf="pf")

@app.route("/portf")
def portf():
    with open("./templates/pf.pdf", "rb") as pdf:
        binary_pdf = pdf.read()
    response = make_response(binary_pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=portfolio.pdf'
    return response

@app.route("/prob")
def prob():
    port = random.randint(49152,65535)
    os.popen(f"docker run --rm -p {port}:80 shock")
    return render_template("index.html", link="http://www.dpp0900.com:" + str(port))


'''index'''

'''
@app.route("/")
def index():
    return "Hello World!", 200
'''
    
'''ip'''
@app.route("/ip")
def ip():
    with open("iplogger/mylog.log", "a") as LOG:
        LOG.write(request.environ['REMOTE_ADDR'] + "\n")
    #return "<script>location.href=\"https://www.google.com\";</script>"
    return jsonify({'ip': request.remote_addr}), 200

'''iplogger'''
def refreshlogs():
    logger_sql = Sql("iplogger")
    deadtimes = logger_sql.selectFromDB("deadtime")
    for deadtime in deadtimes:
        if deadtime[0] < time.time():
            logger_sql.deleteFromDB("id={}".format(deadtime[0]))
@app.route("/iplogger")
def iplogger():
    refreshlogs()
    if request.method == "GET":
        return render_template("iplogger/index.html")
    elif request.method == "POST":
        logger_sql = Sql("iplogger")
        logger_sql.data["id"] = random.randint(0,9999999)
        while logger_sql.data in [item for t in logger_sql.selectFromDB("id") for item in t]:
            logger_sql.data["id"] = random.randint(0,9999999)
        logger_sql.data["redirect"] = request.form["redirect"]
        logger_sql.data["time"] = time.time()
        logger_sql.data["deadtime"] = logger_sql.data["time"] + 18000
        logger_sql.data["password"] = random.randint(1000,9999)
        logger_sql.insertIntoDB()
        with open("iplogger/" + str(logger_sql.data["id"]) + ".log", "w") as log_setup:
            log_setup.writelines("==========YourLog==========")
        return render_template("iplogger/codeReturn.html", pscode=logger_sql.data["password"], link="http://www.dpp0900.com/redirect?cd=" + str(logger_sql.data["id"]))
    return "", 404
@app.route("/logcheck")
def logcheck():
    refreshlogs()
    if request.method == "GET":
        return render_template("iplogger/logcheck.html"), 200
    elif request.method == "POST":
        logger_sql = Sql("iplogger")
        password = str(logger_sql.selectFromDB("id", "password=" + str(request.form["cod"]))[0][0])
        if (password + ".log") in os.listdir("iplogger/"):
            return open("iplogger/" + password + ".log", "r").read().replace("\n", "</br>"), 200
    return "", 404
@app.route("/redirec/<int:redirect_id>")
def log_redirect(redirect_id):
    refreshlogs()
    if redirect_id + ".log" in os.listdir("iplogger/"):
        logger_sql = Sql("iplogger")
        redirect_db = logger_sql.selectFromDB("redirect","id="+redirect_id)
        with open("iplogger/" + redirect_id + ".log", "a") as log:
            log.writelines(time.strftime("%Y-%m-%d || %H:%M:%S", time.localtime(time.time())) + " || " + request.environ["REMOTE_ADDR"])
        return redirect(redirect_db[0]), 302
    else:
        return "", 404
    
'''link'''
def insertLink(name, label, link, host, count):
    link_sql = Sql("links")
    uid = random.randint(10000000,90000000)
    #while uid in link_sql.selectFromDB("id")[0]:
    #    uid = random.randint(10000000,90000000)
    link_sql.data = {
        "id" : uid,
        "name" : name,
        "label" : label,
        "link" : link,
        "host" : host,
        "count" : count
    }
    link_sql.insertIntoDB()
    return uid
@app.route("/link/<username>/<int:uid>")
def link(uid,username):
    link_sql = Sql("links")
    dt = link_sql.selectFromDB(where="id="+str(uid))[0]
    dt = {"name" : json.loads(dt[2].replace("'", "\"")), "link" : json.loads(dt[3].replace("'", "\"")), "host" : json.loads(dt[4].replace("'", "\"")), "count": dt[5]}
    if dt:
        return render_template("link/linkPreview.html", name=username, dt=dt)
    else:
        return "", 404
@app.route("/link/setup", methods=["GET", "POST"])
def linkSetup():
    if request.method == "GET":
        return render_template("link/linkSetup.html"), 200
    elif request.method == "POST":
        filterExp = MakeExpression(FilterRes["AllowEnglish"], FilterRes["AllowNumber"], FilterRes["AllowUnderScoreDot"])
        if filterExp.findall(request.form["name"]):
            return render_template("link/linkSetup.html", err="영어, 숫자, _, .만 입력 가능합니다."), 200
        if request.form["name"] == "" or request.form["name"] == " ":
            return render_template("link/linkSetup.html", err="이름이 비워져있습니다."), 200
        reqdict = dict(request.form)
        linkcount = len(reqdict.keys())//2
        dt = {"name" : [], "link" : [], "host" : [], "count": 0}
        for i in range(0, linkcount):
            filterExp = MakeExpression(FilterRes["AllowEnglish"], FilterRes["AllowNumber"], FilterRes["AllowUnderScoreDot"], FilterRes["AllowKorean"])
            if filterExp.findall(reqdict["linkNM-"+str(i)]):
                return render_template("link/linkSetup.html", err="영어, 숫자, _, ., 한글만 입력 가능합니다."), 200
            if reqdict["linkNM-"+str(i)] == "" or reqdict["linkNM-"+str(i)] == " ":
                return render_template("link/linkSetup.html", err="주소이름이 비워저있습니다."), 200
            filterExp = re.compile(URLexpression)
            if filterExp.findall(reqdict["url-"+str(i)]):
                return render_template("link/linkSetup.html", err="주소가 잘못되었습니다."), 200
            if reqdict["url-"+str(i)] == "" or reqdict["url-"+str(i)] == " ":
                return render_template("link/linkSetup.html", err="주소가 비워져있습니다."), 200
            if reqdict["linkNM-"+str(i)] == reqdict["url-"+str(i)]:
                return render_template("link/linkSetup.html", err="주소이름과 주소가 동일합니다."), 200
            dt["name"].append(reqdict["linkNM-"+str(i)])
            dt["link"].append(reqdict["url-"+str(i)])
            dt["host"].append("http://" + reqdict["url-"+str(i)].split("/")[2])
            dt["count"] = linkcount
        randid = insertLink(reqdict["name"], str(dt["name"]).replace("\'","\""), str(dt["link"]).replace("\'","\""), str(dt["host"]).replace("\'","\""),str(dt["count"]).replace("\'","\""))
        return render_template("link/linkPreview.html", name=reqdict["name"], dt=dt, setupBol=True, randid=randid), 200
    return "", 404
'''test'''
@app.route("/test")
def test():
    return "test", 200

#-----Run-----#
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80)
