#importing libraries
from flask import Flask
from flask import request
import Caller
import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta

MonthDict = {"January": 1, "February": 2, "March": 3,"April" : 4, "May": 5, "June": 6, "July": 7, "August": 8, "September":9, "October": 10, "November": 11, "Decembre": 12}
conn = Caller.ConnectingDB()

#calling by name
app = Flask(__name__)

#creating api for quickreport information (A3 format)
@app.route("/quickreport", methods=['GET'])
def quickreport():
    wonum = request.args.get('wonum')
    try:
        ResponseQR = QuerySelect("SELECT wonum,workorder.crewid,workorder.description AS workorder_description,asset.description AS asset_description,asset.assetnum,tm_eqdwntime,tm_lndwntime,to_char(startdate, 'yyyy-mm-dd hh24:mi:ss'),ticket.ticketid FROM maximo_sap.workorder INNER JOIN maximo_sap.asset ON maximo_sap.workorder.assetnum = maximo_sap.asset.assetnum INNER JOIN maximo_sap.ticket ON workorder.wonum = ticket.origrecordid WHERE wonum = '"+wonum+"' FETCH FIRST 1 ROWS ONLY")[0]
        ResponseEvents = QuerySelect("SELECT description, to_char(eventdatetime, 'yyyy-mm-dd hh24:mi:ss') as date FROM maximo_sap.plusgseqofevents WHERE ticketid = '"+ResponseQR['ticketid']+"'")
        ResponseWHY = QuerySelect("SELECT WHY FROM maximo_sap.plusginvcausean WHERE ticketid ='"+ResponseQR['ticketid']+"'")
        ResponseCM = QuerySelect("SELECT tm_cmid,tm_cmtype,description,ticketid FROM maximo_sap.tm_cm WHERE ticketid = '"+ResponseQR['ticketid']+"'")
        Response = { "Report": [ResponseQR] , "Events":ResponseEvents, "Why": ResponseWHY, "CM": ResponseCM}
    except:
        Response= {}
    return Response

@app.route("/PMReport", methods=['GET'])
def PMRoute():
    try:
        Y = request.args.get('Y')
        Month = str(request.args.get('Month'))
        GetMonthNum = str(MonthDict[Month]).zfill(2)
        input_dt = datetime(2000, int(GetMonthNum), 1)
        res = calendar.monthrange(input_dt.year, input_dt.month)
        startdate = (datetime.strptime(Y+"-"+GetMonthNum+"-"+str(res[1]), '%Y-%m-%d') - relativedelta(months=1, days=7)).strftime("%Y-%m-%d")
        finaldate = (datetime.strptime(Y+"-"+GetMonthNum+"-"+str(res[1]), '%Y-%m-%d') + relativedelta(days= -7)).strftime("%Y-%m-%d")
        ResponseData = QuerySelect("Select description, pmnum, reportdate, status, wopriority, tm_condforwork from maximo_sap.workorder where reportdate >= '"+startdate+"' and reportdate <= '"+finaldate+"' and SPLIT_PART(glaccount, '+', 3) = 'M9120M' and siteid = 'BCT1' and not(tm_condforwork = 'UP') and pmnum is not null ")
    except:
        return {}
    return {"Data" : ResponseData}

@app.route("/GetTotalExpenses", methods=['GET'])
def getTotalExpenses():
    try:
        FY = int(request.args.get('FY'))-1
        CurrencyData = str(request.args.get('CurrencyData'))
        CC = str(request.args.get('CC'))
        Month = str(request.args.get('Month'))
        GetMonthNum = str(MonthDict[Month]).zfill(2)
        input_dt = datetime(2000, int(GetMonthNum), 1)
        res = calendar.monthrange(input_dt.year, input_dt.month)
        day = res[1]
        ResponseData = QuerySelect("SELECT DISTINCT ON (mrline.mrnum, mrline.mrlinenum) mrline.qty, mrline.linecost AS linecost, a_invreserve.description, matusetrans.tm_sakto AS account, a_invreserve.tm_droppoint AS cc, a_invreserve.requesteddate AS fecha FROM maximo_sap.a_invreserve LEFT JOIN maximo_sap.mrline ON a_invreserve.mrnum = mrline.mrnum AND a_invreserve.mrlinenum = mrline.mrlinenum LEFT JOIN maximo_sap.matusetrans ON a_invreserve.mrnum = matusetrans.mrnum AND a_invreserve.mrlinenum = matusetrans.mrlinenum WHERE requesteddate >= '"+str(FY)+"-04-01' AND requesteddate <= '"+str(FY+1)+"-03-31' AND a_invreserve.tm_droppoint in ("+CC+") AND a_invreserve.tm_status = 'CONFIRMED' UNION SELECT poline.orderqty AS qty, poline.linecost AS linecost, poline.description, poline.tm_sakto AS account, poline.tm_kostl AS cc, poline.enterdate AS fecha FROM maximo_sap.poline WHERE poline.enterdate >='"+str(FY)+"-04-01' AND poline.enterdate <='"+str(FY+1)+"-03-31' AND poline.tm_kostl in ("+CC+") AND poline.tm_elikz IS NULL")
        ResData = {"Data": ResponseData}
    except:
        #ResData= {"Data": 0}
        ResData = {}
    return ResData

@app.route("/Ping", methods = ['GET'])
def Ping():
    try:
        QuerySelect("SELECT 1")
        return {}
    except:
        return {}

def QuerySelect(QUERY):
    global conn
    try:
        TemporalConnection = Caller.CreateConnection(conn)
        TemporalConnection.execute(QUERY)
        Response = TemporalConnection.fetchall()
        TemporalConnection.close()
    except Exception as ex:
        conn = Caller.ConnectingDB()
        Response = {"Error": ex}
    return Response

#python -m venv .venv
#----->>>> source .venv/Scripts/activate 
#----->>>> flask --app MaximoAPI run --host=0.0.0.0 --port=5000