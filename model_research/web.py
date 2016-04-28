from flask import Flask,request, render_template
from main import *
from DateOperator import *
import requests

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/portfolio_map", methods=['POST'])
def portfolio_map():
    module_type = request.form['ModuleType']
    start_time = request.form['startTime']
    end_time = request.form['endTime']
    week_dual = request.form['weekDual']
    week_dual_number = int(week_dual)
    module_type_number = int(module_type)

    asset_str = ['VTI','VEA','VWO','VTIP','VCIT','BNDX','VNQ','FXI']
    lengh1 = 5

    # /////////////////更新redis//////////////////
    # for x in asset_str:
    #     updateRedis(x, lengh1)

    # date_time = ['2015-03-01', '2015-06-01', '2015-09-01', '2015-12-01', '2016-03-01']
    date_time = []

    dateOperator = DateOperator()
    while start_time <= end_time:
        date_time.append(start_time)
        start_time = dateOperator.days(start_time, week_dual_number*7)

    year_len = 3
    point_number = 9
    point_no = module_type_number-1

    weights_date_time = [0.]*len(date_time)

    for x in range(len(date_time)):
        weights_date_time[x] = fun1(asset_str, date_time[x], year_len, point_number, point_no)

    # for x in weights_date_time:
    #     for y in range(len(x)):
    #         print(x[y])

    return render_template("index.html", assets=asset_str, weights=weights_date_time, dateTime=date_time)

if __name__ == "__main__":
    app.run(host="0.0.0.0")