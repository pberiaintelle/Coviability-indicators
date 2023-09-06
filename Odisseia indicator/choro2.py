# -*- coding: utf-8 -*-

import json

import pandas as pd
import geopandas as gpd
import plotly
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import Dash, dcc, html, Output, Input, State, callback, dcc, html
#C:/Users/pablo/Documents/IRD/src/
# Import data 
od = pd.read_csv('od_pct_change2.csv', encoding='cp1252')
#od_mean = pd.read_csv('od_mean.csv', encoding='cp1252')
with open('C:/Users/pablo/Documents/IRD/src/order_mun.geojson') as json_data:
    mun_data = json.load(json_data)
    # Convert the GeoJSON data to a GeoDataFrame
mun = gpd.GeoDataFrame.from_features(mun_data['features'])
# Reproject to EPSG 3857 (Web Mercator)
mun.crs = 'epsg:3857'
# Make a copy of the 'CD_MUN' column
mun['CD_MUN_COPY'] = mun['CD_MUN']
mun = mun.set_index('CD_MUN')
#mun = gpd.read_file('order_mun.geojson')
#mun = mun.set_index('CD_MUN')
# mapbox token
mapbox_accesstoken = 'pk.eyJ1IjoicGFibG9iZXJpYWluIiwiYSI6ImNsbGdtaWYwNjEzNjEzZXFodnc5MDU3ODYifQ.45XStASb0dbFZMGU0yGTMw'

# This is the part to create plotly fig
########################################################
ods=od['NM_MUN'].str.title().tolist()
# Convert 'Year' to string as it will be used as text for the x-axis labels
#od['Year'] = od['Year'].astype(str)

pl_deep = [
    [0.0, 'rgb(255, 102, 102)'],   # Light Red
    [0.1, 'rgb(255, 128, 102)'],  # Light Orange-red
    [0.2, 'rgb(255, 153, 102)'],  # Light Orange
    [0.3, 'rgb(255, 179, 102)'],  # Light Orange-yellow
    [0.4, 'rgb(255, 204, 102)'],  # Light Yellow
    [0.5, 'rgb(204, 255, 153)'],  # Light Yellow-green
    [0.6, 'rgb(153, 255, 153)'],  # Light Green-yellow
    [0.7, 'rgb(102, 255, 102)'],  # Light Green
    [0.8, 'rgb(102, 204, 102)'],  # Light Green with a hint of blue
    [0.9, 'rgb(102, 153, 102)'],  # Light Green with more blue
    [1.0, 'rgb(102, 255, 102)']   # Light Green
]

Types = ['Mortality','DAP Person','Amount of employed people','% basic education']    

trace1 = []    
    
# Municipalities order should be the same as "id" passed to location
for q in Types:
    trace1.append(go.Choroplethmapbox(
        geojson = mun.__geo_interface__,
        locations = od.CD_MUN,
        z = od[q].tolist(),
        colorscale = pl_deep,
        text = ods, 
        colorbar = dict(thickness=20, ticklen=3),
        marker_line_width=0, marker_opacity=0.7,
        visible=False,
        subplot='mapbox1',
        hovertemplate = "<b>%{text}</b><br><br>" +
                        "Value: %{z}<br>" +
                        "<extra></extra>")) # "<extra></extra>" means we don't display the info in the secondary box, such as trace id.
    
trace1[0]['visible'] = True

trace2 = []    
    
# Suburbs order should be the same as "id" passed to location
for q in Types:
    trace2.append(go.Bar(
        x=od[q],  # Using the data directly without sorting
        y=od['NM_MUN'].str.title().tolist(),
        xaxis='x2',
        yaxis='y2',
        marker=dict(
            color='rgba(91, 207, 135, 0.3)',
            line=dict(
                color='rgba(91, 207, 135, 2.0)',
                width=0.5),
        ),
        visible=False,
        name='name'.format(q),
        orientation='h',
    ))
 
trace2[0]['visible'] = True


# Paraiba latitude and longitude values
latitude = -7
longitude = -35

layout = go.Layout(
    title = {'text': 'Socio-economical indicators per municipality',
    		 'font': {'size':28, 
    		 		  'family':'Arial'}},
    autosize = True,
    
    mapbox1 = dict(
        domain = {'x': [0.3, 1],'y': [0, 1]},
        center = dict(lat=latitude, lon=longitude),
        accesstoken = mapbox_accesstoken, 
        zoom = 8),

    xaxis2={
        'zeroline': False,
        "showline": False,
        "showticklabels":True,
        'showgrid':True,
        'domain': [0, 0.25],
        'side': 'left',
        'anchor': 'x2',
    },
    yaxis2={
        'domain': [0.4, 0.9],
        'anchor': 'y2',
        'autorange': 'reversed',
    },
    margin=dict(l=20, r=20, t=70, b=70),
    width=1000,
    height=800,
    paper_bgcolor='rgb(204, 204, 204)',
    plot_bgcolor='rgb(204, 204, 204)',
)
layout.update(updatemenus=list([
    dict(x=0,
         y=1,
         xanchor='left',
         yanchor='middle',
         buttons=list([
             dict(
                 args=['visible', [True, False, False, False]],
                 label='Mortality',
                 method='restyle'
                 ),
             dict(
                 args=['visible', [False, True, False, False]],
                 label='DAP - Pessoa Física',
                 method='restyle'
                 ),
             dict(
                 args=['visible', [False, False, True, False]],
                 label='Amount of employed people',
                 method='restyle'
                 ),
             dict(
                 args=['visible', [False, False, False, True]],
                 label='% basic education',
                 method='restyle'
                )
            ]),
        )]))

fig=go.Figure(data=trace2 + trace1, layout=layout)
#For the time series visualization per Municipality
ts = pd.read_csv('odisseia_ts.csv', encoding='cp1252')
def plot_line_chart(data, municipio_codigo, title):
    # Filter the DataFrame for the specified municipio_codigo
    selected_municipio = data[data['municipio_codigo'] == municipio_codigo]
    # Create the line chart using Plotly Express
    fig = px.line(selected_municipio, x='ano', y='valor', color='variavel_nome', markers=True)
    fig.update_layout(title= title, xaxis_title="Time", yaxis_title="Value", legend_title="Select one indicator")
    return fig
#####################################################################
# This is the part to initiate Dash app

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children=''),

    dcc.Graph(
        id='mapbox1',
        figure=fig
    ),

    html.Div(children='''
        Data source from Universidade Federal da Paraíba/ODISSEIA Project @Jul 2023
    '''),
    
    dcc.Graph(figure={}, id='my-graph',
              style={'width': '100%', 'display': 'inline-block'})
])
##calback
@callback(
    Output(component_id='my-graph', component_property='figure'),
    Input(component_id='mapbox1', component_property='clickData'),
    #State(component_id='example-graph-1', component_property='figure'),
    prevent_initial_call=True
)
def update_graph(clickData):
    if clickData:
        municipio_codigo = clickData['points'][0]['location']
        title = clickData['points'][0]['text']
        fig = plot_line_chart(ts, municipio_codigo,title)
        return fig
    return dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True)
