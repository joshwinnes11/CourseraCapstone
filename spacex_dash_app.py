# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv'
spacex_df = pd.read_csv(url)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

options = [{'label':'All Sites','value':'ALL'}]

unique_sites = set()

for loc in zip(spacex_df['Launch Site']):
    if loc not in unique_sites:
        unique_sites.add(loc)
        site = {'label':loc, 'value':loc}
        options.append(site)


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options = options,
                                            placeholder = 'Select a Launch Site',
                                            value = 'ALL',
                                            searchable = True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min = 0,
                                                max = 10000,
                                                step = 1000,
                                                value = [min_payload, max_payload]
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', 
        names='Launch Site', 
        title='Successful Launches Split by Launch Site')
        return fig
    else:
        pie_data = pd.DataFrame(spacex_df.groupby(['Launch Site','class'])['class'].count())
        pie_data2 = pie_data.loc[entered_site, :]
        fig = px.pie(
            pie_data2,
            names = 'class',
            values = 'class',
            title = f'Successful launches for {entered_site[0]}'
        )
        return fig
        
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown',component_property='value'),Input(component_id='payload-slider', component_property='value')])
def get_success_payload_scatter_chart(entered_site, slider):
    min_value, max_value = slider
    if entered_site == 'ALL':
        filtered_data = spacex_df[(spacex_df['Payload Mass (kg)'] <= max_value) & (spacex_df['Payload Mass (kg)']>= min_value)]
        fig = px.scatter(
            filtered_data,
            x = 'Payload Mass (kg)',
            y = 'class',
            title = 'Payload Mass (kg) vs. Mission Success for All Locations',
            color = 'Booster Version Category'
        )
        return fig
    else:
        filtered_data = spacex_df[(spacex_df['Payload Mass (kg)'] <= max_value) & (spacex_df['Payload Mass (kg)']>= min_value)&(spacex_df['Launch Site']==entered_site[0])]
        # further_filtered = filtered_data[filtered_data['Launch Site']==entered_site]
        fig = px.scatter(
            filtered_data,
            x='Payload Mass (kg)',
            y = 'class',
            title = f'Payload Mass (kg) vs. Mission Success for {entered_site[0]}',
            color = 'Booster Version Category'
        )
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
