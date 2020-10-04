from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask import Response
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
import os
import pandas as pd
import io
import gev_func

app = Flask(__name__)

# Index
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        req = request.form
        
        #username = req.get("username")
        
        #xx = request.files["inputData"]
        #print(xx)
        
        if(request.files):
            inputFile = request.files["inputData"]
            stream = io.StringIO(inputFile.stream.read().decode("UTF8"), newline=None)
            df = pd.read_csv(stream)
            df.to_csv(os.path.join("temp","inputData.csv"), index=False)
            return render_template('visualizeInput.html', params = req, inputData = df, sampleData = df[:100])
        
        """
        
        # Below is the skeleton for retrieving  what settings the user has selected at Home page
        # Get Parameter 1
        param1 = req.get("param1")
        # Get Parameter 2
        param2 = req.get("param2")
        # Get Return Period Parameter
        return_Period = req.get("return_Period")
        
        print(param1)
        print(param2)
        print(return_Period)
        
        if(param1 == "precipitation" and param2 == "MeV")
            # If user selected precipitation with MeV
            return render_template('create_new_html.html')
        else(param1 == "flood" and param2 == "GeV")
            return render_template('create_other_html.html')
        else .....
        
        """
        
    return render_template('home.html')


# Visualizes Input data as rows
@app.route('/visualizeInput', methods=["GET", "POST"])
def visualizeInput():
    return render_template('visualizeInput.html')

#Shows the charts
@app.route('/plotCalculations', methods=["GET", "POST"])
def plotCalculations():    
    df = pd.read_csv(os.path.join("temp", "inputData.csv"))
    maxima, gev_ffc, T_target = gev_func.get_gev_params(data=df)
    fig_json = gev_func.get_plotly_charts(maxima, gev_ffc, T_target)
    
    return render_template('plotCalculations.html', plot=fig_json)
    
# About
@app.route('/about')
def about():
    return render_template('about.html')

# Downloads Output file
@app.route("/downloadOutput")
def downloadOutput():
    df = pd.read_csv(os.path.join("temp", "inputData.csv"))
    maxima, gev_ffc, T_target = gev_func.get_gev_params(data=df)
    df = gev_func.convt_to_df(T_target,gev_ffc)  
    
    return Response(
        df.to_csv(),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=output.csv"})

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
