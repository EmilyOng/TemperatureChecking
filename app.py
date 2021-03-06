from flask import Flask, render_template, redirect, url_for, request, session
import os
import sqlite3
import requests
from dotenv import load_dotenv


project_folder = os.path.expanduser("~/TemperatureChecking")
load_dotenv(os.path.join(project_folder, ".env"))

API_KEY = "a621f645307c47129920cf7858d1dffe"

connection = sqlite3.connect("Temperatures.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS 'Temperature' ('Kelvin' REAL NOT NULL, 'Celcius' REAL NOT NULL);")
connection.commit()
connection.close()

def database (type, command, additional=None):
    result = None
    connection = sqlite3.connect("Temperatures.db")
    cursor = connection.cursor()
    if type == "INSERT":
        cursor.execute(command, additional)
        connection.commit()
    else:
        cursor.execute(command)
    if type == "SELECT":
        result = cursor.fetchall()
    connection.close()
    return result

def get_graph ():
    result = database("SELECT", "SELECT * FROM Temperature")
    result_k = [temp[0] for temp in result]
    result_c = [temp[1] for temp in result]
    return result_k, result_c

def fetch_news ():
    response = requests.get("https://newsapi.org/v2/everything?q=(virus OR wuhan OR coronavirus)&language=en&sortBy=publishedAt&apiKey="+API_KEY)
    articles = response.json()["articles"]
    return articles

# def get_updates ():
#     url = "https://www.moh.gov.sg/2019-ncov-wuhan"
#     with urllib.request.urlopen(url) as response:
#         html = response.read()

#     soup = BeautifulSoup(html, "html.parser")
#     parent = soup.find(id="ContentPlaceHolder_contentPlaceholder_C009_Col00")
#     updates = {}
#     updates["Latest"] = parent.find("table")
#     return updates


app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", default=False)

@app.route("/", methods=["GET"])
def request_processor ():
    articles = fetch_news()
    if "error_message" in session:
        error_message = session["error_message"]
        session.pop("error_message")
        result_k, result_c = get_graph()
        return render_template("index.html", error_message=error_message,
                                result=[result_k, result_c], articles=articles)
    elif "postal_code" in session:
        postal_code = session["postal_code"]
        session.pop("postal_code")
        return render_template("index.html", show_location=True, postal_code=postal_code, tab="active",
                                articles=articles)
    elif "temperature_processor" in session:
        danger = session["temperature_processor"]["danger"]
        temp = session["temperature_processor"]["temp"]
        units = session["temperature_processor"]["units"]
        session.pop("temperature_processor")
        if danger:
            border_color = "red"
            message_title = "Danger Zone"
        else:
            border_color = "green"
            message_title = "Safe Zone"
        kelvin = (units != "Kelvin") * (-273.0) + temp
        celcius = (units != "Celcius") * (273.0) + temp
        database("INSERT", "INSERT INTO Temperature (Kelvin, Celcius) VALUES (?, ?)", (kelvin, celcius))
        temp = str(temp) + (units=="Kelvin")*"K" + (units=="Celcius")*"\u00B0C"
        result_k, result_c = get_graph()
        return render_template("index.html", border_color=border_color,
                                message_title=message_title, temp=temp, result=[result_k, result_c],
                                articles=articles)
    result_k, result_c = get_graph()
    return render_template("index.html", result=[result_k, result_c], articles=articles)

@app.route("/", methods=["GET", "POST"])
def index ():
    if request.form:
        if "units" and "temperature" in request.form:
            units = request.form["units"]
            temperature = request.form["temperature"]
            # Check temperature data type
            try:
                temperature = float(temperature)
                if (units == "Celcius" and not 35.0 <= temperature <= 45.0) or (units == "Kelvin" and not 308.15 <= temperature <= 318.15):
                    error_message = "Expected a temperature reading between 35.0\u00B0C celcius (308.15 Kelvin) and 45.0\u00B0C celcius (318.15 Kelvin)."
                    session["error_message"] = error_message
                    pass
                keys = list(request.form.keys())
                keys.remove("units")
                keys.remove("temperature")
                symptoms = [request.form[symptom] for symptom in keys]
                danger = ((temperature + (units=="Kelvin") * 273.0) >= 38.0) or len(symptoms) >= 2
                session["temperature_processor"] = {"danger": danger,
                                                    "temp": temperature,
                                                    "symptoms": symptoms,
                                                    "units": units}
            except:
                error_message = "Expected a temperature reading in float/integer."
                session["error_message"] = error_message
        if "postal_code" in request.form:
            session["postal_code"] = request.form["postal_code"]

        return redirect(url_for("request_processor"))

    result_k, result_c = get_graph()
    articles = fetch_news()
    return render_template("index.html", result=[result_k, result_c], articles=articles)


if __name__ == "__main__":
    app.run()
