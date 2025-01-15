import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the data into a pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv", delimiter=",") 

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(id='site-dropdown',
                                            options=[
                                                {'label': 'All Sites', 'value': 'ALL'}
                                            ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()], 
                                            value='ALL',
                                            placeholder="Select a Launch Site",
                                            searchable=True
                                            ),
                                html.Br(),

                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=spacex_df['Payload Mass (kg)'].max(), step=1000,
                                                value=[min(spacex_df['Payload Mass (kg)']), max(spacex_df['Payload Mass (kg)'])]),

                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Callback for the pie chart
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', 
                    names='Launch Site', 
                    title='Success Count for all launch sites')
        return fig
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        df1 = filtered_df.groupby(['Launch Site', 'class']).size().reset_index(name='class count')
        fig = px.pie(df1, values='class count', 
                    names='class', 
                    title=f'Success Count for site {entered_site}')
        return fig

# Callback for the scatter plot
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def scatter(entered_site, payload):
    filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload[0],payload[1])]
    if entered_site=='ALL':
        fig = px.scatter(filtered_df,x='Payload Mass (kg)', y='class',
        color="Booster Version Category",
        title='Correlation between Payload and Success for All Sites')
        return fig
    else:
        fig = px.scatter(filtered_df[filtered_df['Launch Site']==entered_site],x='Payload Mass (kg)', y='class',
        color="Booster Version Category",
        title=f'Correlation between Payload and Success for site {entered_site}')
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()