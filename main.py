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
#import plotly.express as px
import plotly.graph_objects as go
#import seaborn as sns

#sns.set_context('talk')
#palette = sns.color_palette(sns.husl_palette(20, l=.6, s=.9)) # 20 countries max
palette = ("#023FA5","#7D87B9","#BEC1D4","#D6BCC0","#BB7784", "#000000",
            "#4A6FE3","#8595E1","#B5BBE3","#E6AFB9","#E07B91","#D33F6A",
            "#11C638","#8DD593","#C6DEC7","#EAD3C6","#F0B98D","#EF9708",
            "#0FCFC0","#9CDED6","#D5EAE7","#F3E1EB","#F6C4E1","#F79CD4")

import dash
import dash_html_components as html
import dash_core_components as dcc
# import pickle
# import copy
from dash.dependencies import Input, Output, State
import textwrap

from get_data import get_data
from Tracking_Covid19_World_Confirmed import plot_confirmed
from Tracking_Covid19_World_Deaths import plot_deaths
from Tracking_Covid19_World_Mortality import plot_mortality
from Tracking_Covid19_World_Daily import plot_daily_deaths

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

df = get_data()
countries = df.country.unique().tolist()
countries.sort()
color_map = dict(zip(countries, palette))
color_map['South Africa'] = '#d4af37'
startlist = ('Brazil', 'Germany', 'India', 'Italy', 'Japan', 'South Korea', 'France', 'Sweden',
             'Russia', 'South Africa', 'Spain',  'US', 'Austrailia', 'Canada', 'China', 'UK')

country_options = [
    {"label": str(country), "value": str(country)} for country in countries
]

# Create app layout
app.layout = html.Div(
    [
#        dcc.Store(id="aggregate_data"),
#        dcc.Store(id='session', storage_type='session'),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("Beal Logo.png"),
                            id="plotly-image",
                            style={
                                "height": "140px",
                                "width": "auto",
                                "margin-bottom": "5px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [                
                        html.H1(
                            "Tracking Covid19 in South Africa",
                            style={"margin-bottom": "0px"},
                        ),
                        html.H4(
                            "Comparing with the World", style={"margin-top": "0px"}
                        ),                          
                    ],
                    className="one-half column",
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
                    id="cross-filter-options",
                ),
                html.Div(
                    [                                                     
                        html.Div(
                            [dcc.Graph(id="graph")],
                            id="GraphContainer",
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
    if chart_selector == 'dailydeaths':
        note = (textwrap.dedent('''
        **Note on Daily Number of Deaths:**  
        * Each country selected has a seperate plot.
        * Numbers on the y axis is not on a log scale and each graph has its own range.  
        * Notice the 7 to 8 day cycle of infections'''))
    return note


if __name__ == '__main__':
    app.run_server(debug=True)