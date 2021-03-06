import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from pyvis.network import Network
from IPython.core.display import display, HTML
import geopandas as gpd
from plotly import graph_objects as go
import numpy as np

st.title('Domestic Flights in the U.S.A.')

st.write('Please explore the dataset about domestic flights around the United States from 2005-2009!')

flights_df = pd.read_csv('Final_flights.csv')

Airport = st.sidebar.multiselect('Choose an Airport', flights_df['Origin_airport'].unique())

airport_flights = flights_df[['Origin_airport', 'Flights']]
grouped = airport_flights.groupby('Origin_airport').sum()

airport_passengers = flights_df[['Origin_airport', 'Passengers']]
grouped_pass = airport_passengers.groupby(['Origin_airport']).sum()

airport_date_flights = flights_df[['Origin_airport', 'Revenue_Passenger_Mile']]
grouped_date_flights = airport_date_flights.groupby('Origin_airport').sum()

df = grouped.loc[grouped.index.isin(Airport)]
df1 = grouped_pass[grouped_pass.index.isin(Airport)]
df2 = grouped_date_flights[grouped_date_flights.index.isin(Airport)]

##################################################
st.write('Here is a map of all the airports!')

fig, ax = plt.subplots(figsize=(100,15))

continents = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

continents[continents['continent']=='North America'].plot(color='lightgrey',
ax=ax)

flights_df.plot(x = 'Org_airport_long', y = 'Org_airport_lat', kind = 'scatter', c = 'red',
                colormap = 'YlOrRd', title = 'Airports Across the U.S.', ax=ax)

ax.set(xlim=(-160,0), ylim=(0,70), autoscale_on = False)

ax.grid(b=True, alpha=0.5)

st.pyplot(fig)

##################################################
st.write('How are they all connected? Let us look at our connected graph!')
fig = go.Figure()

source_to_dest = zip(flights_df['Org_airport_lat'], 
                    flights_df['Dest_airport_lat'], 
                    flights_df['Org_airport_long'], 
                    flights_df['Dest_airport_long'], 
                    flights_df['Flights'])

for slat, dlat, slon, dlon, num_flights in source_to_dest:
    fig.add_trace(go.Scattergeo(
        lat = [slat,dlat],
        lon = [slon, dlon],
        mode = 'lines',
        line = dict( width= num_flights/100, color = 'lime')
    ))
cities = flights_df['Origin_city'].values.tolist()+flights_df['Destination_city'].values.tolist()
airports = flights_df['Origin_airport'].values.tolist()+flights_df['Destination_airport'].values.tolist()
scatter_hover_data = [airport + ' : ' + city for city, airport in zip(cities, airports)]

fig.add_trace(
    go.Scattergeo(
        lon = flights_df['Org_airport_long'].values.tolist()+flights_df['Dest_airport_long'].values.tolist(),
        lat = flights_df['Org_airport_lat'].values.tolist()+flights_df['Dest_airport_lat'].values.tolist(),
        hoverinfo = 'text',
        text = scatter_hover_data,
        mode = 'markers',
        marker = dict(size=10, color='orangered', opacity=0.1))
    )

fig.update_layout(title_text = 'Connection Map Showing Flights between U.S. Cities',
                height=700, width=900,
                margin={'t':0, 'b':0, 'l':0, 'r':0, 'pad':0},
                showlegend=False,
                geo = dict(scope='usa'))

st.plotly_chart(fig)

################################################################
st.write('Select some airports and compare their flights!')
fig, ax = plt.subplots()
ax.bar(df.index, df['Flights'])
ax.set_xticklabels(Airport, rotation = 45)
ax.set_xlabel('Airport Code')
ax.set_ylabel('Number of Flights')
ax.set_title('Number of Departing Flights from Airports from 2005-2009', fontweight='bold')
st.pyplot(fig)

# ################################################################
st.write('Select some airports and compare their revenue (Y axis is by a factor of 1e10)')
fig, ax = plt.subplots()
ax.bar(df2.index,df2['Revenue_Passenger_Mile'])
ax.set_xticklabels(Airport, rotation= 45)
ax.set_xlabel('Airport')
ax.set_ylabel('Passenger Revenue Per Mile')
ax.set_title('Total Revenue per Mile per Airport', fontweight='bold')
st.pyplot(fig)

##################################################################
st.write('Select some airports and compare their number of passengers! (Y-axis is at a factor of 1e7)')
fig, ax = plt.subplots()
ax.bar(df1.index, df1['Passengers'])
ax.set_xticklabels(Airport, rotation= 45)
ax.set_xlabel('Airport')
ax.set_ylabel('Number of Passengers')
ax.set_title('Annual Passenger Traffic at Airport')
st.pyplot(fig)

##################################################################
