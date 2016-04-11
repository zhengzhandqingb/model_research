from flask import Flask,request,url_for,render_template
app = Flask(__name__)

@app.route("/test")
def test():
    return "success"


@app.route("/history_model")
def history_model():
    model_id = request.form['model_id']
    date = request.form["date"]
    #todo 计算模型




if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5000)