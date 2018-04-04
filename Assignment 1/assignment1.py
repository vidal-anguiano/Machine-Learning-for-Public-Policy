import sqlite3
from sodapy import Socrata
import pandas as pd
import config
import censusgeocode as cg
import requests
from census import Census
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
init_notebook_mode(connected=True)

CLIENT = Socrata("data.cityofchicago.org", config.key)
CENSUS = Census(config.census_key)



resource_ids = {'graffiti': 'cdmx-wzbz',
			    'vacant': '7nii-7srd',
			    'lights': 't28b-ys7j'}

metadata = {'B02001_002E' : {'name': "white", 'dtype' : 'int'},
                      'B02001_003E' : {'name': "black", 'dtype' : 'int'},
                      'B02001_005E' : {'name': "asian", 'dtype' : 'int'},
                      'B03001_003E' : {'name': "hispanic", 'dtype' : 'int'},
                      'B19013_001E' : {'name': "median_income", 'dtype' : 'int'},
                      'B19301_001E' : {'name': "per_capita_income", 'dtype' : 'int'},
                      'B23025_001E' : {'name': "total_employed", 'dtype' : 'int'},
                      'B23025_005E' : {'name': "unemployed", 'dtype' : 'int'},
                      'B17001_002E' : {'name': "poverty", 'dtype' : 'int'},
                      'B01003_001E' : {'name': "total_population", 'dtype' : 'int'},
                      'B25077_001E' : {'name': "median_home_value", 'dtype' : 'int'}}

def get_FIPS(latitude, longitude):
    try:
        FTC_API_format = "https://geo.fcc.gov/api/census/block/find?format=json&latitude={latitude}&longitude={longitude}"
        return requests.get(FTC_API_format.format(longitude=longitude, latitude=latitude)).json()['Block']['FIPS']
    except Exception as e:
        print(e)
        return np.nan

def acs5_census_download(variables, metadata, conn, state = '17', county = '031'):
	census_data = CENSUS.acs5.get(variables, geo={'for': 'block group: *',
                       'in': 'state:{} county:{}'.format(state,county)})
	census_data_df = pd.DataFrame(census_data)
	census_data_df.to_csv('census_data.csv', header = False, index = False)

	print(create_census_ddl(variables, metadata, state, county))



def create_census_ddl(variables, metadata, state, county):
	query = """CREATE TABLE census_{}_{} (""".format(state, county)
	for var in variables:
		query += '\n{} {},'.format(metadata[var]['name'], metadata[var]['dtype'])
	query += '''\nblock_group INT, \ncounty INT, \nstate INT, \ntract INT)'''

	return query

def barplot(df,x, y, title = '', xlabel = '', ylabel = '', subtitle = '', xsize = 14):
    data = [go.Bar(
            x=list(df[x]),
            y=list(df[y]),
            # text=list(df[y]),
            textposition = 'outside',
            opacity=1)]

    layout = go.Layout(
            title='<b>'+title+'</b><br>'+subtitle,
            xaxis=dict(
                title= xlabel,
                tickfont=dict(
                    size=xsize,
                    color='rgb(107, 107, 107)'
                )
            ),
            yaxis=dict(
                title=ylabel,
                titlefont=dict(
                    size=16,
                    color='rgb(107, 107, 107)'
                ),
                tickfont=dict(
                    size=14,
                    color='rgb(107, 107, 107)'
                )
            ),
           )

    fig = go.Figure(data=data, layout=layout)
    iplot(fig, filename='basic-bar')

