# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 14:55:56 2023

@author: pablo
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import dash
import dash_leaflet as dl
from jupyter_dash import JupyterDash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import json

# Load your data
indi = pd.read_csv('Indicator_table_updated.csv', encoding='cp1252')
lu = pd.read_csv('Land_use.csv')
lu_agg = pd.read_csv('lu_agg.csv')
lu_f = pd.read_csv('Land_use_forestbox.csv')
lu_u = pd.read_csv('Land_use_urbanbox.csv')
bd = pd.read_csv('iNaturalistGbifIUCNmerged.csv', encoding='cp1252')

# Read GeoJSON files
with open('forestbbox.geojson') as f1:
    geojson_data1 = json.load(f1)

with open('urbanbbox.geojson') as f2:
    geojson_data2 = json.load(f2)

# Extract coordinates from GeoJSON
coords1 = geojson_data1['features'][0]['geometry']['coordinates'][0]
coords2 = geojson_data2['features'][0]['geometry']['coordinates'][0]

lon1, lat1 = zip(*coords1)  # Unzip coordinates
lon2, lat2 = zip(*coords2)  # Unzip coordinates

# Create a scattermapbox figure
fig = go.Figure()

# Add scatter points to the figure
scatter_trace = go.Scattermapbox(
    mode="markers",
    lon=[-35], lat=[-7],
    marker={'size': 20, 'color': "cyan"}
)

# Add GeoJSON polygons to the figure
geojson_trace1 = go.Scattermapbox(
    mode="none",
    lon=lon1,
    lat=lat1,
    fill="toself",
    fillcolor='green',
    line={'color': "green"},
    name="Forest sample"
)
fig.add_trace(geojson_trace1)

geojson_trace2 = go.Scattermapbox(
    mode="none",
    lon=lon2,
    lat=lat2,
    fill="toself",
    fillcolor="red",
    line={'color': "red"},
    name="Urban sample"
)
fig.add_trace(geojson_trace2)

# Create a new scattermapbox trace for the border polygon
border_geojson_trace = go.Scattermapbox(
    mode="lines",  # Set mode to "lines" for the border
    lon=[-34.740, -34.740, -35.633, -35.633, -34.740],  # Specify the coordinates of the polygon
    lat=[-6.369, -7.709, -7.709, -6.369, -6.369],
    line={'color': "royalblue"},  # Set color for the border
    name="Entire study area"
)
fig.add_trace(border_geojson_trace)

# Update layout of the figure
fig.update_layout(
    mapbox={
        'style': "stamen-terrain",
        'center': {'lon': -35, 'lat': -7},
        'zoom': 8,
    },
    margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
    width=700,
    height=800
)
############################################################################################################33
# Initialize the Dash app
app = JupyterDash(external_stylesheets=[dbc.themes.SLATE])

# Define controls
controls = dbc.Card(
    [dbc.FormGroup(
        [
            dbc.Label("Options"),
            dcc.RadioItems(
                id="display_figure",
                options=[
                    {'label': 'None', 'value': 'Nope'},
                    {'label': 'Aggregated classes', 'value': 'Figure1'},
                    {'label': 'All classes', 'value': 'Figure2'},
                    {'label': 'Forest sample', 'value': 'Figure3'},
                    {'label': 'Urban sample', 'value': 'Figure4'}
                ],
                value='Nope',
                labelStyle={'display': 'inline-block', 'width': '10em', 'line-height': '0.5em'}
            )
        ],
    ),
        dbc.FormGroup(
            [dbc.Label(""), ]
        ),
    ],
    body=True,
    style={'font-size': 'large'})

# App layout
app.layout = html.Div([
    html.H1(children='Potential Coviability indicators'),
    html.P(children='Ideal project for the coast of Paraiba'),

    html.Div([
        html.Div([
            html.H3('Sunburst chart'),
            dcc.Graph(
                id='sunburst-plot',
                figure=px.sunburst(indi, path=['CI', 'Domain', 'Theme', 'Subcategory', 'Indicator', 'Time series'],
                                   values='Values',
                                   hover_data=['Data source', 'Spatial resolution'],
                                   maxdepth=3, width=700, height=800, color_discrete_sequence=px.colors.qualitative.Dark24)
            )
        ], className='six columns'),

        html.Div([
            html.H3('Map view'),
            html.Div(className='map-container', style={'width': '700px', 'height': '800px'}, children=[
                dcc.Graph(
                    id='scatter-map',
                    figure=fig  # Use the previously created scattermapbox figure
                )
            ])
        ], className='six columns')
    ], className='row'),

   # dcc.Graph(id='line-plot'),

    dbc.Container(
        [
            html.H1("Land use change"),
            html.Hr(),
            dbc.Row([
                dbc.Col([controls], xs=4),
                dbc.Col([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id="landuse")),
                    ])
                ]),
            ]),
            html.Br(),
            dbc.Row([
            ]),
        ],
        fluid=True,
    ),
])

# Define the callback for the "predictions" graph
@app.callback(
    Output("landuse", "figure"),
    [Input("display_figure", "value")]
)
def make_graph(display_figure):

    if 'Nope' in display_figure:
        fig = go.Figure()
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          yaxis = dict(showgrid=False, zeroline=False, tickfont = dict(color = 'rgba(0,0,0,0)')),
                          xaxis = dict(showgrid=False, zeroline=False, tickfont = dict(color = 'rgba(0,0,0,0)')))
        return fig

    if 'Figure1' in display_figure:
        fig = px.line(lu_agg, x='year', y='area', color='Merged', markers=True)
       # fig.add_traces(go.Scatter(name=y, x=df[x], y=df[y2], mode = 'lines'))
        fig.update_layout(
            title="Aggregated LU Over Time",
            xaxis_title="Time",
           yaxis_title="Area km2",
           legend_title="LU classes",
           )

    # prediction trace
    if 'Figure2' in display_figure:
       fig = px.line(lu, x='year', y='area', color='LandUse', markers=True)
        #fig.add_traces(go.Scatter(name=y, x=df.index, y=df[y2], mode = 'lines'))
       fig.update_layout(
            title="Land Use Over Time",
            xaxis_title="Time",
           yaxis_title="Area km2",
           legend_title="LU classes",
           )

    if 'Figure3' in display_figure:
        fig = px.line(lu_f, x='year', y='area', color='LandUse', markers=True)
       # fig.add_traces(go.Scatter(name=y, x=df[x], y=df[y2], mode = 'lines'))
        fig.update_layout(
            title="Forest area LU Over Time",
            xaxis_title="Time",
           yaxis_title="Area km2",
           legend_title="LU classes",
           )
    if 'Figure4' in display_figure:
        fig = px.line(lu_u, x='year', y='area', color='LandUse', markers=True)
       # fig.add_traces(go.Scatter(name=y, x=df[x], y=df[y2], mode = 'lines'))
        fig.update_layout(
            title="Urban area LU Over Time",
            xaxis_title="Time",
           yaxis_title="Area km2",
           legend_title="LU classes",
           )

    # Aesthetics
    fig.update_layout(margin= {'t':30, 'b':0, 'r': 0, 'l': 0, 'pad': 0})
    fig.update_layout(hovermode = 'x')
    fig.update_layout(showlegend=True, legend=dict(x=1,y=0.85))
    fig.update_layout(uirevision='constant')
   

    return(fig)

# Run the app
if __name__ == '__main__':
    #app.run_server(mode='external', port = 8005)
    app.run_server(debug=True)

#app.run_server(mode='external', port = 8005)