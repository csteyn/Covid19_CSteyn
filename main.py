# Import required libraries
import sys
import math
import requests
import pandas as pd
import numpy as np

from datetime import datetime
from datetime import timedelta, date
import io

import plotly
import plotly.graph_objects as go

# palette = ("#023FA5","#7D87B9","#BEC1D4","#D6BCC0","#BB7784", "#000000",
#             "#4A6FE3","#8595E1","#B5BBE3","#E6AFB9","#E07B91","#D33F6A",
#             "#11C638","#8DD593","#C6DEC7","#EAD3C6","#F0B98D","#EF9708",
#             "#0FCFC0","#9CDED6","#D5EAE7","#F3E1EB","#F6C4E1","#F79CD4")

palette = ('#FF9966', '#FBE7B2', '#926F5B', '#FE6F5E', '#A3E3ED', '#0066FF', '#9999CC', '#0095B6',
            '#6456B7', '#C62D42', '#FB607F', '#AF593E', '#FF7034', '#E97451', '#A9B2C3', #'#FFFF99',
            '#00CC99', '#FFA6C9', '#DA3287', '#02A4D3', '#FF9966', '#B94E48', '#DA8A67', '#93CCEA',
            '#FFB7D5', '#DB5079', '#FED85D', '#1560BD', '#EDC9AF', '#614051', '#CCFF00', '#63B76C',
            '#FFCBA4', '#5FA777', '#C154C1', '#C45655', '#E6BE8A', '#FCD667', '#9DE093', '#8B8680',
            '#01A368', '#F1E788', '#FF00CC', '#B94E48', '#4F69C6', '#A50B5E', '#29AB87', #'#B0E313',
            '#FFFF66', '#FBAED2', '#FFB97B', '#F653A6', '#AAF0D1', '#CA3435', '#8D90A1', '#E77200',
            '#C32148', '#F091A9', '#FEBAAD', '#003366', '#1AB385', '#C54B8C', '#0066CC', '#FF9933',
            '#B5B35C', '#FF681F', '#E29CD2', '#2D383A', '#FF6037', '#009DC4', '#FFCBA4', '#C3CDE6',
            '#FDD7E4', '#01796F', '#FF66FF', '#843179', '#003366', '#652DC1', '#9678B6', '#FF00CC',
            '#FF355E', '#D27D46', '#FF33CC', '#E30B5C', '#ED0A3F', '#FF3F34', '#BB3385', '#00CCCC',
            '#6B3FA0', '#FF91A4', '#FD0E35', '#66FF66', '#93DFB8', '#9E5B40', '#837050', '#33CC99',
            '#FF6FFF', '#C9C0BB', '#76D7EA', '#ECEBBD', '#FFCC33', '#FE4C40', '#FA9D5A', '#FC80A5',
            '#D9D6CF', '#FD0E35', '#00755E', '#DEA681', '#6CDAE7', '#66FF66', '#FF6037', '#FF6FFF',
            '#FD5B78', '#FFFF66', '#FFFF66', '#8359A3', '#F7468A', '#FF9980', '#803790', '#FFFFFF',
            '#7A89B8', '#FF3399', '#FD5B78', '#C9A0DC', '#FBE870', '#C5E17A', '#FFAE42')

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import textwrap

#sys.path.append(os.path.join(os.path.dirname(__file__),  "scripts"))
from scripts.get_data import get_data
from scripts.Tracking_Covid19_World_Confirmed import plot_confirmed
from scripts.Tracking_Covid19_World_Deaths import plot_deaths
from scripts.Tracking_Covid19_World_Mortality import plot_mortality
from scripts.Tracking_Covid19_World_Daily import plot_daily_confirmed
from scripts.Tracking_Covid19_World_Daily_Deaths import plot_daily_deaths

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

df = get_data()

countries = df.country.unique().tolist()
countries.sort()
color_map = dict(zip(countries, palette))
color_map['South Africa'] = '#d4af37'
startlist = ('Germany', 'India', 'Italy', 'South Korea','Sweden',
             'Russia', 'South Africa', 'Spain',  'US', 'Austrailia', 'UK')

country_options = [
    {"label": str(country), "value": str(country)} for country in countries
]

# Create app layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("Carl Steyn_EmailSignature.jpg"),
                            id="plotly-image",
                            style={'height':'100%', 'width':'100%'},
                            # style={
                            #     "width": "auto"                                
                            # },
                        )
                    ],
                    className="three columns",
                ),
                html.Div(
                    [                
                        html.H1(
                            "Tracking COVID19 in South Africa",
                            style={"margin-bottom": "0px"},
                        ),
                        html.H4(
                            "Comparing with the World", style={"margin-top": "0px"}
                        ),                          
                    ],
                    className="two-thirds column",
                    id="title",
                ),                
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "5px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H5(
                            "Explore",
                            style = {'text-align': 'center' },                                                       
                        ),  
                        html.P(
                            "Select chart type:",
                            className="control_label",
                            style = {'font-weight': 'bold'},
                        ),                        
                        dcc.RadioItems(
                            id="chart_selector",
                            options=[
                                {"label": "Confirmed Cases ", "value": "confirmed"},
                                {"label": "Deaths ", "value": "deaths"},
                                {"label": "Mortaility ", "value": "mortality"},
                                {"label": "Daily Confirmed Cases", "value": "dailyconfirmed"},
                                {"label": "Daily Deaths", "value": "dailydeaths"}
                            ],
                            value="confirmed",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        html.P(
                            "Select the countries:",
                            className="control_label",
                            style = {'font-weight': 'bold'},
                        ), 
                        html.P(
                            "Note: Do not select too many countries at once as this makes the interactive plots slow",
                            className="control_label",
                            style ={'font-size': '9px', 'font-style': 'italic', 'padding': '0px'},                           
                        ),                          
                        dcc.Checklist(
                            id="country_selector",
                            options=country_options,
                            value= startlist,
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Markdown(
                            id="note",
                            className="control_label",
                            
                        ),                                              
                    ],
                    className="pretty_container three columns",
                    # id="cross-filter-options",
                ),
                html.Div(
                    [                                                     
                        html.Div(
                            [dcc.Graph(id="graph", style={"height": "100%", "width": "100%"})],
                            id="count_graph",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="nine columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

@app.callback(
    Output('graph', 'figure'),
    [Input('chart_selector', 'value'),
     Input('country_selector', 'value'),
     ])
def update_graph(chart_selector, country_selector):
    global df
    df_select = df.loc[(df.country.isin (list(country_selector)))]

    if chart_selector == 'confirmed':
        return plot_confirmed(df_select,color_map)
    if chart_selector == 'deaths':
        return plot_deaths(df_select, color_map)
    if chart_selector == 'mortality':
        return plot_mortality(df_select, color_map)
    if chart_selector == 'dailyconfirmed':
        return plot_daily_confirmed(df_select, color_map)
    if chart_selector == 'dailydeaths':
        return plot_daily_deaths(df_select, color_map)   

@app.callback(Output("note", "children"), [Input('chart_selector', 'value')])
def change_note(chart_selector):
    if chart_selector == 'confirmed':
        note = (textwrap.dedent('''
        **Note on Confirmed Cases:**  
        * _Press play to see how the graph evolves over time. Move the slider to go to a specific date._  
        * Both axes are presented on a log scale.  
        * The loglog plot indicate that during the growth phase of the virus that each 10 daily new confirmed cases results in an increase of a 100 total confirmed cases.
        When the curve moves away form the line this is an indication that the measures taken are starting to work.'''))
        
    if chart_selector == 'deaths':
        note = (textwrap.dedent('''
        **Note on Deaths:**  
        * _Press play to see how the graph evolves over time.  Move the slider to go to a specific date._  
        * Both axes are presented on a log scale.  
        * The loglog plot indicate that during the growth phase of the virus that each 1 daily new death results in an increase of 10 total deaths.
        When the curve moves away form the line this is an indication that the measures taken are starting to work.'''))
    if chart_selector == 'mortality':
        note = (textwrap.dedent('''
        **Note on Mortality:**  
        * _Press play to see how the graph evolves over time._  
        * The median value presented is only for the countries selected.  
        * When playing over time the country with the highest mortality rate is dynamically moved to the top.'''))
    if chart_selector == 'dailyconfirmed':
        note = (textwrap.dedent('''
        **Note on Daily Number of Confirmed Cases:**  
        * Numbers on the y axis is not on a log scale and each graph has its own range.  
        * Notice the 7 to 8-day cycle of infections'''))
    if chart_selector == 'dailydeaths':
        note = (textwrap.dedent('''
        **Note on Daily Number of Deaths:**  
        * Numbers on the y axis is not on a log scale and each graph has its own range.  
        * Notice there is also a 7 to 8-day cycle although less prominent than for infections'''))
    return note


if __name__ == '__main__':
    app.server(host='0.0.0.0', port=8080, debug=False)
    # app.run_server(debug=True)