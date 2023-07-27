import pandas as pd
import dash
import dash_html_components as html 
import dash_core_components as dcc 
from dash.dependencies import Input, Output, State 
import plotly.graph_objects as go 
import plotly.express as px 
from dash import no_update

app = dash.Dash(__name__)

app.config.suppress_callback_exceptions = True
spacex_data = pd.read_csv('spacex_launch_dash.csv',
                            encoding = 'ISO-8859-1',
                            )
max_payload = spacex_data['Payload Mass (kg)'].max()
min_payload = spacex_data['Payload Mass (kg)'].min()

# Layout Section of Dash
app.layout = html.Div(children = [
    html.H1('SpaceX Launch Records Dashboard',
            style = {'textAlign': 'center','color':'#503D36','front-size':40}),
    html.Div([
        dcc.Dropdown(id='site-dropdown',
                    options=[
                        {'label': 'All Sites', 'value': 'All'},
                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                    ],
                    value='ALL',
                    placeholder='Select a Launch Site here',
                    searchable=True, 
                    style={'width':'80%','padding':'3px','font-size':'20px','text-align-last':'center'}),
        html.Br(),

        html.Div(dcc.Graph(id='success-pie-chart')),

        html.Br(),

        html.P('Payload Range (Kg):'),

        dcc.RangeSlider(id='payload-slider',
                        min = 0, 
                        max = 10000, 
                        step = 1000,
                        value=[min_payload,max_payload]
        ),

        html.Div(dcc.Graph(id='success-payload-scatter-chart')),

    ]),
    
])
# add callback decorator
@app.callback(Output(component_id='success-pie-chart',component_property='figure'),
                Input(component_id='site-dropdown',component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_data
    if entered_site == 'ALL':
        fig = px.pie(filtered_df,values='class',
        names='Launch Site',
        title='Success count for each launch site')
        return fig
    else:
        filtered_df = spacex_data[spacex_data['Launch Site']] == entered_site
        filtered_df=filtered_df.groupby(['Launch Site','class']).size().reset_index(name='class count')
        fig=px.pie(filtered_df,values='class count',names='class',title=f"Total Success Launches for site {entered_site}")
        return fig

@app.callback(Output(component_id='success-payload-scatter-chart',component_property='figure'),
                [Input(component_id='site-dropdown',component_property='value'),
                Input(component_id='payload-slider',component_property='value')])
def get_scatter_chart(entered_site,payload):
    filtered_df = spacex_data[spacex_data['Payload Mass (kg)'].between(payload[0],payload[1])]
    # thought reusing filtered_df may cause issues, but tried it out of curiosity and it seems to be working fine
    
    if entered_site=='ALL':
        fig=px.scatter(filtered_df,x='Payload Mass (kg)',y='class',color='Booster Version Category',title='Success count on Payload mass for all sites')
        return fig
    else:
        fig=px.scatter(filtered_df[filtered_df['Launch Site']==entered_site],x='Payload Mass (kg)',y='class',color='Booster Version Category',title=f"Success count on Payload mass for site {entered_site}")
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()