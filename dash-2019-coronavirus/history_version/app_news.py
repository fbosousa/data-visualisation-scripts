# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math 

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html 
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

################################################################################
#### Data processing
################################################################################
# Import xlsx file and store each sheet in to a df list
xl_file = pd.ExcelFile('./data.xlsx',)

dfs = {sheet_name: xl_file.parse(sheet_name) 
          for sheet_name in xl_file.sheet_names}

# Data from each sheet can be accessed via key
keyList = list(dfs.keys())

# Data cleansing
for key, df in dfs.items():
    dfs[key].loc[:,'Confirmed'].fillna(value=0, inplace=True)
    dfs[key].loc[:,'Deaths'].fillna(value=0, inplace=True)
    dfs[key].loc[:,'Recovered'].fillna(value=0, inplace=True)
    dfs[key]=dfs[key].astype({'Confirmed':'int64', 'Deaths':'int64', 'Recovered':'int64'})
    # Change as China for coordinate search
    dfs[key]=dfs[key].replace({'Country/Region':'Mainland China'}, 'China')
    dfs[key]=dfs[key].replace({'Province/State':'Queensland'}, 'Brisbane')
    dfs[key]=dfs[key].replace({'Province/State':'New South Wales'}, 'Sydney')
    dfs[key]=dfs[key].replace({'Province/State':'Victoria'}, 'Melbourne')
    # Add a zero to the date so can be convert by datetime.strptime as 0-padded date
    dfs[key]['Last Update'] = '0' + dfs[key]['Last Update']
    # Convert time as Australian eastern daylight time
    dfs[key]['Date_last_updated_AEDT'] = [datetime.strptime(d, '%m/%d/%Y %H:%M') for d in dfs[key]['Last Update']]
    dfs[key]['Date_last_updated_AEDT'] = dfs[key]['Date_last_updated_AEDT'] + timedelta(hours=16)

# Add coordinates for each area in the list for the latest table sheet
# To save time, coordinates calling was done seperately
# Import the data with coordinates
dfs[keyList[0]]=pd.read_csv('{}_data.csv'.format(keyList[0]))

# Save numbers into variables to use in the app
confirmedCases=dfs[keyList[0]]['Confirmed'].sum()
deathsCases=dfs[keyList[0]]['Deaths'].sum()
recoveredCases=dfs[keyList[0]]['Recovered'].sum()

# Construct confirmed cases dataframe for line plot
DateList = []
ChinaList =[]
OtherList = []

for key, df in dfs.items():
    dfTpm = df.groupby(['Country/Region'])['Confirmed'].agg(np.sum)
    dfTpm = pd.DataFrame({'Code':dfTpm.index, 'Confirmed':dfTpm.values})
    dfTpm = dfTpm.sort_values(by='Confirmed', ascending=False).reset_index(drop=True)
    DateList.append(df['Date_last_updated_AEDT'][0])
    ChinaList.append(dfTpm['Confirmed'][0])
    OtherList.append(dfTpm['Confirmed'][1:].sum())
    
df_confirmed = pd.DataFrame({'Date':DateList,
                             'Mainland China':ChinaList,
                             'Other locations':OtherList})
# Select the latest data from a given date
df_confirmed['date_day']=[d.date() for d in df_confirmed['Date']]
df_confirmed=df_confirmed.groupby(by=df_confirmed['date_day'], sort=False).transform(max).drop_duplicates(['Date'])
df_confirmed['Total']=df_confirmed['Mainland China']+df_confirmed['Other locations']
df_confirmed=df_confirmed.reset_index(drop=True)

# Construct new dataframe for 24-hour window case difference
DateList = []
ChinaList =[]
OtherList = []

for key, df in dfs.items():
    dfTpm = df.groupby(['Country/Region'])['Confirmed'].agg(np.sum)
    dfTpm = pd.DataFrame({'Code':dfTpm.index, 'Confirmed':dfTpm.values})
    dfTpm = dfTpm.sort_values(by='Confirmed', ascending=False).reset_index(drop=True)
    DateList.append(df['Date_last_updated_AEDT'][0])
    ChinaList.append(dfTpm['Confirmed'][0])
    OtherList.append(dfTpm['Confirmed'][1:].sum())
    
df_confirmed_diff = pd.DataFrame({'Date':DateList,
                                  'Mainland China':ChinaList,
                                  'Other locations':OtherList}) 
df_confirmed_diff['Total']=df_confirmed_diff['Mainland China']+df_confirmed_diff['Other locations']

# Calculate differenec in a 24-hour window
for index, _ in df_confirmed_diff.iterrows():
    # Calculate the time differnece in hour
    diff=(df_confirmed_diff['Date'][0] - df_confirmed_diff['Date'][index]).total_seconds()/3600
    # find out the latest time after 24-hour
    if diff >= 24:
        break
plusConfirmedNum = df_confirmed_diff['Total'][0] - df_confirmed_diff['Total'][index]
plusPercentNum1 = (df_confirmed_diff['Total'][0] - df_confirmed_diff['Total'][index])/df_confirmed_diff['Total'][index]

# Construct recovered cases dataframe for line plot
DateList = []
ChinaList =[]
OtherList = []

for key, df in dfs.items():
    dfTpm = df.groupby(['Country/Region'])['Recovered'].agg(np.sum)
    dfTpm = pd.DataFrame({'Code':dfTpm.index, 'Recovered':dfTpm.values})
    dfTpm = dfTpm.sort_values(by='Recovered', ascending=False).reset_index(drop=True)
    DateList.append(df['Date_last_updated_AEDT'][0])
    ChinaList.append(dfTpm['Recovered'][0])
    OtherList.append(dfTpm['Recovered'][1:].sum())
    
df_recovered = pd.DataFrame({'Date':DateList,
                             'Mainland China':ChinaList,
                             'Other locations':OtherList}) 
# Select the latest data from a given date
df_recovered['date_day']=[d.date() for d in df_recovered['Date']]
df_recovered=df_recovered.groupby(by=df_recovered['date_day'], sort=False).transform(max).drop_duplicates(['Date'])
df_recovered['Total']=df_recovered['Mainland China']+df_recovered['Other locations']
df_recovered=df_recovered.reset_index(drop=True)

# Construct new dataframe for 24-hour window case difference
DateList = []
ChinaList =[]
OtherList = []

for key, df in dfs.items():
    dfTpm = df.groupby(['Country/Region'])['Recovered'].agg(np.sum)
    dfTpm = pd.DataFrame({'Code':dfTpm.index, 'Recovered':dfTpm.values})
    dfTpm = dfTpm.sort_values(by='Recovered', ascending=False).reset_index(drop=True)
    DateList.append(df['Date_last_updated_AEDT'][0])
    ChinaList.append(dfTpm['Recovered'][0])
    OtherList.append(dfTpm['Recovered'][1:].sum())
    
df_recovered_diff = pd.DataFrame({'Date':DateList,
                                  'Mainland China':ChinaList,
                                  'Other locations':OtherList}) 
df_recovered_diff['Total']=df_recovered_diff['Mainland China']+df_confirmed_diff['Other locations']

# Calculate differenec in a 24-hour window
for index, _ in df_recovered_diff.iterrows():
    # Calculate the time differnece in hour
    diff=(df_recovered_diff['Date'][0] - df_recovered_diff['Date'][index]).total_seconds()/3600
    # find out the latest time after 24-hour
    if diff >= 24:
        break
plusRecoveredNum = df_recovered_diff['Total'][0] - df_recovered_diff['Total'][index]
plusPercentNum2 = (df_recovered_diff['Total'][0] - df_recovered_diff['Total'][index])/df_recovered_diff['Total'][index]

# Construct death case dataframe for line plot
DateList = []
ChinaList =[]
OtherList = []

for key, df in dfs.items():
    dfTpm = df.groupby(['Country/Region'])['Deaths'].agg(np.sum)
    dfTpm = pd.DataFrame({'Code':dfTpm.index, 'Deaths':dfTpm.values})
    dfTpm = dfTpm.sort_values(by='Deaths', ascending=False).reset_index(drop=True)
    DateList.append(df['Date_last_updated_AEDT'][0])
    ChinaList.append(dfTpm['Deaths'][0])
    OtherList.append(dfTpm['Deaths'][1:].sum())
    
df_deaths = pd.DataFrame({'Date':DateList,
                          'Mainland China':ChinaList,
                          'Other locations':OtherList})
# Select the latest data from a given date
df_deaths['date_day']=[d.date() for d in df_deaths['Date']]
df_deaths=df_deaths.groupby(by='date_day', sort=False).transform(max).drop_duplicates(['Date'])
df_deaths['Total']=df_deaths['Mainland China']+df_deaths['Other locations']
df_deaths=df_deaths.reset_index(drop=True)

# Construct new dataframe for 24-hour window case difference
DateList = []
ChinaList =[]
OtherList = []

for key, df in dfs.items():
    dfTpm = df.groupby(['Country/Region'])['Deaths'].agg(np.sum)
    dfTpm = pd.DataFrame({'Code':dfTpm.index, 'Deaths':dfTpm.values})
    dfTpm = dfTpm.sort_values(by='Deaths', ascending=False).reset_index(drop=True)
    DateList.append(df['Date_last_updated_AEDT'][0])
    ChinaList.append(dfTpm['Deaths'][0])
    OtherList.append(dfTpm['Deaths'][1:].sum())
    
df_deaths_diff = pd.DataFrame({'Date':DateList,
                                  'Mainland China':ChinaList,
                                  'Other locations':OtherList}) 
df_deaths_diff['Total']=df_deaths_diff['Mainland China']+df_deaths_diff['Other locations']

# Calculate differenec in a 24-hour window
for index, _ in df_deaths_diff.iterrows():
    # Calculate the time differnece in hour
    diff=(df_deaths_diff['Date'][0] - df_deaths_diff['Date'][index]).total_seconds()/3600
    # find out the latest time after 24-hour
    if diff >= 24:
        break
plusDeathNum = df_deaths_diff['Total'][0] - df_deaths_diff['Total'][index]
plusPercentNum3 = (df_deaths_diff['Total'][0] - df_deaths_diff['Total'][index])/df_deaths_diff['Total'][index]

# Create data table to show in app
# Generate sum values for Country/Region level
dfCase = dfs[keyList[0]].groupby(by='Country/Region', sort=False).sum().reset_index()
dfCase = dfCase.sort_values(by=['Confirmed'], ascending=False).reset_index(drop=True)
# As lat and lon also underwent sum(), which is not desired, remove from this table.
dfCase = dfCase.drop(columns=['lat','lon'])

# Grep lat and lon by the first instance to represent its Country/Region
dfGPS = dfs[keyList[0]].groupby(by=['Country/Region'], sort=False).first().reset_index()
dfGPS = dfGPS[['Country/Region','lat','lon']]

# Merge two dataframes
dfSum = pd.merge(dfCase, dfGPS, how='inner', on='Country/Region')
dfSum = dfSum.replace({'Country/Region':'China'}, 'Mainland China')
# Rearrange columns to correspond to the number plate order
dfSum = dfSum[['Country/Region','Confirmed','Recovered','Deaths','lat','lon']]

# Save numbers into variables to use in the app
latestDate=datetime.strftime(df_confirmed['Date'][0], '%b %d, %Y %H:%M AEDT')
secondLastDate=datetime.strftime(df_confirmed['Date'][1], '%b %d')
daysOutbreak=(df_confirmed['Date'][0] - datetime.strptime('12/31/2019', '%m/%d/%Y')).days

#############################################################################################
#### Start to make plots
#############################################################################################
# Line plot for confirmed cases
# Set up tick scale based on confirmed case number
tickList = list(np.arange(0, df_confirmed['Mainland China'].max()+1000, 10000))

# Create empty figure canvas
fig_confirmed = go.Figure()
# Add trace to the figure
fig_confirmed.add_trace(go.Scatter(x=df_confirmed['Date'], y=df_confirmed['Mainland China'],
                                   mode='lines+markers',
                                   line_shape='spline',
                                   name='Mainland China',
                                   line=dict(color='#921113', width=3),
                                   marker=dict(size=6, color='#f4f4f2',
                                               line=dict(width=1,color='#921113')),
                                   text=[datetime.strftime(d, '%b %d %Y AEDT') for d in df_confirmed['Date']],
                                   hovertext=['Mainland China confirmed<br>{:,d} cases<br>'.format(i) for i in df_confirmed['Mainland China']],
                                   hovertemplate='<b>%{text}</b><br></br>'+
                                                 '%{hovertext}'+
                                                 '<extra></extra>'))
fig_confirmed.add_trace(go.Scatter(x=df_confirmed['Date'], y=df_confirmed['Other locations'],
                                   mode='lines+markers',
                                   line_shape='spline',
                                   name='Other Region',
                                   line=dict(color='#eb5254', width=3),
                                   marker=dict(size=6, color='#f4f4f2',
                                               line=dict(width=1,color='#eb5254')),
                                   text=[datetime.strftime(d, '%b %d %Y AEDT') for d in df_confirmed['Date']],
                                   hovertext=['Other region confirmed<br>{:,d} cases<br>'.format(i) for i in df_confirmed['Other locations']],
                                   hovertemplate='<b>%{text}</b><br></br>'+
                                                 '%{hovertext}'+
                                                 '<extra></extra>'))
# Customise layout
fig_confirmed.update_layout(
#    title=dict(
#    text="<b>Confirmed Cases Timeline<b>",
#    y=0.96, x=0.5, xanchor='center', yanchor='top',
#    font=dict(size=20, color="#292929", family="Playfair Display")
#   ),
    margin=go.layout.Margin(
        l=10,
        r=10,
        b=10,
        t=5,
        pad=0
    ),
    yaxis=dict(
        showline=True, linecolor='#272e3e',
        zeroline=False,
        gridcolor='rgba(203, 210, 211,.3)',
        gridwidth = .1,
        tickmode='array',
        # Set tick range based on the maximum number
        tickvals=tickList,
        # Set tick label accordingly
        ticktext=["{:.0f}k".format(i/1000) for i in tickList]
    ),
#    yaxis_title="Total Confirmed Case Number",
    xaxis=dict(
        showline=True, linecolor='#272e3e',
        gridcolor='rgba(203, 210, 211,.3)',
        gridwidth = .1,
        zeroline=False
    ),
    xaxis_tickformat='%b %d',
    hovermode = 'x',
    legend_orientation="h",
#    legend=dict(x=.35, y=-.05),
    plot_bgcolor='#f4f4f2',
    paper_bgcolor='#cbd2d3',
    font=dict(color='#292929')
)

# Line plot for combine cases
# Set up tick scale based on confirmed case number
tickList = list(np.arange(0, df_recovered['Mainland China'].max()+1000, 2000))

# Create empty figure canvas
fig_combine = go.Figure()
# Add trace to the figure
fig_combine.add_trace(go.Scatter(x=df_recovered['Date'], y=df_recovered['Total'],
                                   mode='lines+markers',
                                   line_shape='spline',
                                   name='Total Recovered Cases',
                                   line=dict(color='#168038', width=3),
                                   marker=dict(size=6, color='#f4f4f2',
                                               line=dict(width=1,color='#168038')),
                                   text=[datetime.strftime(d, '%b %d %Y AEDT') for d in df_recovered['Date']],
                                   hovertext=['Total recovered<br>{:,d} cases<br>'.format(i) for i in df_recovered['Total']],
                                   hovertemplate='<b>%{text}</b><br></br>'+
                                                 '%{hovertext}'+
                                                 '<extra></extra>'))
fig_combine.add_trace(go.Scatter(x=df_deaths['Date'], y=df_deaths['Total'],
                                mode='lines+markers',
                                line_shape='spline',
                                name='Total Death Cases',
                                line=dict(color='#626262', width=3),
                                marker=dict(size=6, color='#f4f4f2',
                                            line=dict(width=1,color='#626262')),
                                text=[datetime.strftime(d, '%b %d %Y AEDT') for d in df_deaths['Date']],
                                hovertext=['Total death<br>{:,d} cases<br>'.format(i) for i in df_deaths['Total']],
                                hovertemplate='<b>%{text}</b><br></br>'+
                                              '%{hovertext}'+
                                              '<extra></extra>'))
# Customise layout
fig_combine.update_layout(
    #title=dict(
    #    text="<b>Recovered Cases Timeline<b>",
    #    y=0.96, x=0.5, xanchor='center', yanchor='top',
    #    font=dict(size=20, color="#292929", family="Playfair Display")
    #),
    margin=go.layout.Margin(
        l=10,
        r=10,
        b=10,
        t=5,
        pad=0
    ),
    yaxis=dict(
        showline=True, linecolor='#272e3e',
        zeroline=False,
        gridcolor='rgba(203, 210, 211,.3)',
        gridwidth = .1,
        tickmode='array',
        # Set tick range based on the maximum number
        tickvals=tickList,
        # Set tick label accordingly
        ticktext=["{:.0f}k".format(i/1000) for i in tickList]
    ),
#    yaxis_title="Total Recovered Case Number",
    xaxis=dict(
        showline=True, linecolor='#272e3e',
        gridcolor='rgba(203, 210, 211,.3)',
        gridwidth = .1,
        zeroline=False
    ),
    xaxis_tickformat='%b %d',
    hovermode = 'x',
    legend_orientation="h",
#    legend=dict(x=.35, y=-.05),
    plot_bgcolor='#f4f4f2',
    paper_bgcolor='#cbd2d3',
    font=dict(color='#292929')
)

# Line plot for death rate cases
# Set up tick scale based on confirmed case number
tickList = list(np.arange(0, (df_deaths['Mainland China']/df_confirmed['Mainland China']*100).max(), 0.5))

# Create empty figure canvas
fig_rate = go.Figure()
# Add trace to the figure
fig_rate.add_trace(go.Scatter(x=df_deaths['Date'], y=df_deaths['Mainland China']/df_confirmed['Mainland China']*100,
                                mode='lines+markers',
                                line_shape='spline',
                                name='Mainland China',
                                line=dict(color='#626262', width=3),
                                marker=dict(size=6, color='#f4f4f2',
                                            line=dict(width=1,color='#626262')),
                                text=[datetime.strftime(d, '%b %d %Y AEDT') for d in df_deaths['Date']],
                                hovertext=['Mainland China death rate<br>{:.2f}%'.format(i) for i in df_deaths['Mainland China']/df_confirmed['Mainland China']*100],
                                hovertemplate='<b>%{text}</b><br></br>'+
                                              '%{hovertext}'+
                                              '<extra></extra>'))
fig_rate.add_trace(go.Scatter(x=df_deaths['Date'], y=df_deaths['Other locations']/df_confirmed['Other locations']*100,
                                mode='lines+markers',
                                line_shape='spline',
                                name='Other Region',
                                line=dict(color='#a7a7a7', width=3),
                                marker=dict(size=6, color='#f4f4f2',
                                            line=dict(width=1,color='#a7a7a7')),
                                text=[datetime.strftime(d, '%b %d %Y AEDT') for d in df_deaths['Date']],
                                hovertext=['Other region death rate<br>{:.2f}%'.format(i) for i in df_deaths['Other locations']/df_confirmed['Other locations']*100],
                                hovertemplate='<b>%{text}</b><br></br>'+
                                              '%{hovertext}'+
                                              '<extra></extra>'))

# Customise layout
fig_rate.update_layout(
    margin=go.layout.Margin(
        l=10,
        r=10,
        b=10,
        t=5,
        pad=0
    ),
    yaxis=dict(
        showline=True, linecolor='#272e3e',
        zeroline=False,
        gridcolor='rgba(203, 210, 211,.3)',
        gridwidth = .1,
        tickmode='array',
        # Set tick range based on the maximum number
        tickvals=tickList,
        # Set tick label accordingly
        ticktext=['{:.1f}'.format(i) for i in tickList]
    ),
#    yaxis_title="Total Death Case Number",
    xaxis=dict(
        showline=True, linecolor='#272e3e',
        gridcolor='rgba(203, 210, 211,.3)',
        gridwidth = .1,
        zeroline=False
    ),
    xaxis_tickformat='%b %d',
    hovermode = 'x',
    legend_orientation="h",
#    legend=dict(x=.35, y=-.05),
    plot_bgcolor='#f4f4f2',
    paper_bgcolor='#cbd2d3',
    font=dict(color='#292929')
)

##################################################################################################
#### Start dash app
##################################################################################################

app = dash.Dash(__name__, 
                assets_folder='./assets/',
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, height=device-height, initial-scale=1.0"}
                ]
      )

# Section for Google annlytic #
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-154901818-2"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'UA-154901818-2');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

server = app.server

app.layout = html.Div(style={'backgroundColor':'#f4f4f2'},
    children=[
        html.Div(
            id="header",
            children=[                          
                html.H4(children="Coronavirus (COVID-19) Outbreak Global Cases Monitor"),
                html.P(
                    id="description",
                    children="On Dec 31, 2019, the World Health Organization (WHO) was informed of \
                    an outbreak of “pneumonia of unknown cause” detected in Wuhan City, Hubei Province, China – the \
                    seventh-largest city in China with 11 million residents. As of {}, there are over {:,d} cases \
                    of COVID-19 confirmed globally.\
                    This dash board is developed to visualise and track the recent reported \
                    cases on a daily timescale.".format(latestDate, confirmedCases),
                )         
            ]        
        ),
        html.Div(style={'marginLeft':'1.5%','marginRight':'1.5%','marginBottom':'.5%','height':'50px', 'overflow':'auto'},
          id='note',
          children=[
#              html.P(
#                  children=['⚠️ Source from ', 
#                  html.A('The National Health Commission of China', href='http://www.nhc.gov.cn/yjb/s7860/202002/553ff43ca29d4fe88f3837d49d6b6ef1.shtml'),
#                  ': in its February 14 official report, deducted \
#                  108 previously reported deaths and 1,043 previously reported cases from the total in Hubei Province due to "repeated counting." \
#                  Data have been corrected for these changes.']
#               ),
#              html.P(
#                  children=['⚠️ Source from ', 
#                  html.A('读卖新闻', href='https://www.yomiuri.co.jp/national/20200216-OYT1T50089/'),
#                  ': Diamond Princess cruise confirmed 70 new infections, bringing the total infected cases to 355.']
#               ),
              html.P(
                  children=['⚠️ Source from ',
                            html.A('The Guardian', href='https://www.theguardian.com/world/live/2020/feb/20/coronavirus-live-updates-diamond-princess-cruise-ship-japan-deaths-latest-news-china-infections'),
                            ': two Japanese passengers from Diamond Princess have died, a man and a woman in their 80s, both with an underlying illness.']              
               ),
              html.P(
                  children=['⚠️ Source from ',
                            html.A('Bloomberg', href='https://www.bloomberg.com/news/articles/2020-02-19/china-eyes-hna-takeover-hubei-says-108-new-deaths-virus-update?srnd=premium-asia'),
                            ': South Korea reports first death as outbreak spreads.']
               ),
              html.Div(
                html.P(style={'fontWeight':'bold'},
                    children="Last updated on {}.".format(latestDate)),
               ),
              
          ]
        ),
        html.Div(
            id="number-plate",
            style={'marginLeft':'1.5%','marginRight':'1.5%','marginBottom':'.5%','marginTop':'.5%'},
                 children=[
                     html.Div(
                         style={'width':'24.4%','backgroundColor':'#cbd2d3','display':'inline-block',
                                'marginRight':'.8%','verticalAlign':'top'},
                              children=[
                                  html.H3(style={'textAlign':'center',
                                                 'fontWeight':'bold','color':'#2674f6'},
                                               children=[
                                                   html.P(style={'color':'#cbd2d3','padding':'.5rem'},
                                                              children='xxxx xx xxx xxxx xxx xxxxx'),
                                                   '{}'.format(daysOutbreak),
                                               ]),
                                  html.H5(style={'textAlign':'center','color':'#2674f6','padding':'.1rem'},
                                               children="Days Since Outbreak")                                        
                                       ]),
                     html.Div(
                         style={'width':'24.4%','backgroundColor':'#cbd2d3','display':'inline-block',
                                'marginRight':'.8%','verticalAlign':'top'},
                              children=[
                                  html.H3(style={'textAlign':'center',
                                                 'fontWeight':'bold','color':'#d7191c'},
                                                children=[
                                                    html.P(style={'padding':'.5rem'},
                                                              children='+ {:,d} in the past 24h ({:.1%})'.format(plusConfirmedNum, plusPercentNum1)),
                                                    '{:,d}'.format(confirmedCases)
                                                         ]),
                                  html.H5(style={'textAlign':'center','color':'#d7191c','padding':'.1rem'},
                                               children="Confirmed Cases")                                        
                                       ]),
                     html.Div(
                         style={'width':'24.4%','backgroundColor':'#cbd2d3','display':'inline-block',
                                'marginRight':'.8%','verticalAlign':'top'},
                              children=[
                                  html.H3(style={'textAlign':'center',
                                                       'fontWeight':'bold','color':'#1a9622'},
                                               children=[
                                                   html.P(style={'padding':'.5rem'},
                                                              children='+ {:,d} in the past 24h ({:.1%})'.format(plusRecoveredNum, plusPercentNum2)),
                                                   '{:,d}'.format(recoveredCases),
                                               ]),
                                  html.H5(style={'textAlign':'center','color':'#1a9622','padding':'.1rem'},
                                               children="Recovered Cases")                                        
                                       ]),
                     html.Div(
                         style={'width':'24.4%','backgroundColor':'#cbd2d3','display':'inline-block',
                                'verticalAlign':'top'},
                              children=[
                                  html.H3(style={'textAlign':'center',
                                                       'fontWeight':'bold','color':'#6c6c6c'},
                                                children=[
                                                    html.P(style={'padding':'.5rem'},
                                                              children='+ {:,d} in the past 24h ({:.1%})'.format(plusDeathNum, plusPercentNum3)),
                                                    '{:,d}'.format(deathsCases)
                                                ]),
                                  html.H5(style={'textAlign':'center','color':'#6c6c6c','padding':'.1rem'},
                                               children="Death Cases")                                        
                                       ])
                          ]),
        html.Div(
            id='dcc-plot',
            style={'marginLeft':'1.5%','marginRight':'1.5%','marginBottom':'.35%','marginTop':'.5%'},
                 children=[
                     html.Div(
                         style={'width':'32.79%','display':'inline-block','marginRight':'.8%','verticalAlign':'top'},
                              children=[
                                  html.H5(style={'textAlign':'center','backgroundColor':'#cbd2d3',
                                                 'color':'#292929','padding':'1rem','marginBottom':'0'},
                                               children='Confirmed Case Timeline'),
                                  dcc.Graph(style={'height':'300px'},figure=fig_confirmed)]),
                     html.Div(
                         style={'width':'32.79%','display':'inline-block','marginRight':'.8%','verticalAlign':'top'},
                              children=[
                                  html.H5(style={'textAlign':'center','backgroundColor':'#cbd2d3',
                                                 'color':'#292929','padding':'1rem','marginBottom':'0'},
                                               children='Recovered/Death Case Timeline'),
                                  dcc.Graph(style={'height':'300px'},figure=fig_combine)]),
                     html.Div(
                         style={'width':'32.79%','display':'inline-block','verticalAlign':'top'},
                              children=[
                                  html.H5(style={'textAlign':'center','backgroundColor':'#cbd2d3',
                                                 'color':'#292929','padding':'1rem','marginBottom':'0'},
                                               children='Death Rate (%) Timeline'),
                                  dcc.Graph(style={'height':'300px'},figure=fig_rate)])]),
        html.Div(
            id='dcc-map',
            style={'marginLeft':'1.5%','marginRight':'1.5%','marginBottom':'.5%'},
                 children=[
                     html.Div(style={'width':'66.41%','marginRight':'.8%','display':'inline-block','verticalAlign':'top'},
                              children=[
                                  html.H5(style={'textAlign':'center','backgroundColor':'#cbd2d3',
                                                 'color':'#292929','padding':'1rem','marginBottom':'0'},
                                               children='Latest Coronavirus Outbreak Map'),
                                  dcc.Graph(
                                      id='datatable-interact-map',
                                      style={'height':'500px'},
                                  )
                              ]),
                     html.Div(style={'width':'32.79%','display':'inline-block','verticalAlign':'top'},
                              children=[
                                  html.H5(style={'textAlign':'center','backgroundColor':'#cbd2d3',
                                                 'color':'#292929','padding':'1rem','marginBottom':'0'},
                                               children='Cases by Country/Region'),
                                  dash_table.DataTable(
                                      id='datatable-interact-location',
                                      # Don't show coordinates
                                      columns=[{"name": i, "id": i} for i in dfSum.columns[0:4]],
                                      # But still store coordinates in the table for interactivity
                                      data=dfSum.to_dict("rows"),
                                      row_selectable="single",
                                      #selected_rows=[],
                                      sort_action="native",
                                      style_as_list_view=True,
                                      style_cell={
                                          'font_family':'Arial',
                                          'font_size':'1.5rem',
                                          'padding':'.1rem',
                                          'backgroundColor':'#f4f4f2',
                                      },
                                      fixed_rows={'headers':True,'data':0},
                                      style_table={
                                          'maxHeight':'500px',
                                          #'overflowY':'scroll',
                                          'overflowX':'scroll',
                                      },
                                      style_header={
                                        'backgroundColor':'#f4f4f2',
                                        'fontWeight':'bold'},
                                      style_cell_conditional=[
                                          {'if': {'column_id':'Country/Regions'},'width':'40%'},
                                          {'if': {'column_id':'Confirmed'},'width':'20%'},
                                          {'if': {'column_id':'Recovered'},'width':'20%'},
                                          {'if': {'column_id':'Deaths'},'width':'20%'},
                                          {'if': {'column_id':'Confirmed'},'color':'#d7191c'},
                                          {'if': {'column_id':'Recovered'},'color':'#1a9622'},
                                          {'if': {'column_id':'Deaths'},'color':'#6c6c6c'},
                                          {'textAlign': 'center'}
                                      ],
                                  )
                              ])
                 ]),
        html.Div(style={'marginLeft':'1.5%','marginRight':'1.5%'},
                 children=[
                     html.P(style={'textAlign':'center','margin':'auto'},
                            children=["Data source from ",
                                      html.A('Dingxiangyuan, ', href='https://ncov.dxy.cn/ncovh5/view/pneumonia?sce\
                                      ne=2&clicktime=1579582238&enterid=1579582238&from=singlemessage&isappinstalled=0'),
                                      html.A('Tencent News, ', href='https://news.qq.com//zt2020/page/feiyan.htm#charts'),
                                      'and ', 
                                      html.A('JHU CSSE', href='https://docs.google.com/spreadsheets/d/1yZv9w9z\
                                      RKwrGTaR-YzmAqMefw4wMlaXocejdxZaTs6w/htmlview?usp=sharing&sle=true#'),
                                      " | 🙏 Pray for China, Pray for the World 🙏 |",
                                      " Developed by ",html.A('Jun', href='https://junye0798.com/')," with ❤️"])])

            ])

@app.callback(
    Output('datatable-interact-map', 'figure'),
    [Input('datatable-interact-location', 'derived_virtual_selected_rows')]
)

def update_figures(derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
        
    dff = dfSum
        
    mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

    # Generate a list for hover text display
    textList=[]
    for area, region in zip(dfs[keyList[0]]['Province/State'], dfs[keyList[0]]['Country/Region']):
        
        if type(area) is str:
            if region == "Hong Kong" or region == "Macau" or region == "Taiwan":
                textList.append(area)
            else:
                textList.append(area+', '+region)
        else:
            textList.append(region)

    fig2 = go.Figure(go.Scattermapbox(
        lat=dfs[keyList[0]]['lat'],
        lon=dfs[keyList[0]]['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            color='#ca261d',
            size=dfs[keyList[0]]['Confirmed'].tolist(), 
            sizemin=4,
            sizemode='area',
            sizeref=2.*max(dfs[keyList[0]]['Confirmed'].tolist())/(150.**2),
        ),
        text=textList,
        hovertext=['Comfirmed: {}<br>Recovered: {}<br>Death: {}'.format(i, j, k) for i, j, k in zip(dfs[keyList[0]]['Confirmed'],
                                                                                                    dfs[keyList[0]]['Recovered'],
                                                                                                    dfs[keyList[0]]['Deaths'])],
        hovertemplate = "<b>%{text}</b><br><br>" +
                        "%{hovertext}<br>" +
                        "<extra></extra>")
    )
    fig2.update_layout(
        plot_bgcolor='#151920',
        paper_bgcolor='#cbd2d3',
        margin=go.layout.Margin(l=10,r=10,b=10,t=0,pad=40),
        hovermode='closest',
        transition = {'duration':1000},
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            style="light",
            # The direction you're facing, measured clockwise as an angle from true north on a compass
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=3.684188 if len(derived_virtual_selected_rows)==0 else dff['lat'][derived_virtual_selected_rows[0]], 
                lon=148.374024 if len(derived_virtual_selected_rows)==0 else dff['lon'][derived_virtual_selected_rows[0]]
            ),
            pitch=0,
            zoom=1.2 if len(derived_virtual_selected_rows)==0 else 4
        )
    )

    return fig2

if __name__ == "__main__":
    app.run_server(debug=True)

