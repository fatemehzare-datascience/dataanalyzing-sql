import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Proj
from sqlalchemy import create_engine
from collections import defaultdict
import time
import math
import networkx as nx
import datetime
import collections
%matplotlib inline
from datetime import datetime
import time
import datetime as dt
import community

# CONFIGURATION FOR DATABASE CONNECTION
user = ''
pwd = ''
server = ''
port = ''
database = ''

def get_active_users(b, p):
    '''
    Calculate the number of total possible records using Duty Cycle (DC)
    :param b: battery data set
    :return: battery data set with a column indicating the percentage of data each participant has in relate to the
    number of total possible records
    '''
    # This equation mutiplies the amount of DC per hour (60/5) by the amount of hours per day times a duration 
    # of a month (30 days) collecting data.
    total = (60 / 5) * 24 * 32

    b = b.groupby(['creatorId']).size().reset_index(name='count')
    b = b[b['count'] >= p * total]
    
    return b

engine = create_engine("mysql+pymysql://" + user + ":" + pwd + "@" + server + ":" + port + "/" + database)
s = "SELECT * " \
    "FROM wifi " \
    "WHERE wifi.rssi > -100"
wifi = pd.read_sql(s, engine)

s = "SELECT * " \
    "FROM location " \
    "WHERE location.dutyCycleLevel > -100"
loc = pd.read_sql(s, engine)
bat = pd.read_sql(s, engine)

def agg_dc(df, is_gps):
    '''
    Aggregate the data by Duty Cycle (DC)
    :param df: dataframe with a DC column
    :param is_gps: boolean value informing if this function should check gps or wifi
    :return: df aggregated by DC
    '''
    
    df['timestamp'] = pd.to_datetime(df['timestamp'].dt.round('5min'))
    
    df['epoch']=((df['timestamp'] - dt.datetime(2014,10,6)).dt.total_seconds())/300
    if is_gps:
        df = df.groupby(["creatorId", "epoch"], as_index=False)\
               .agg({"timestamp": "first", "latitude": np.mean, "longitude": np.mean})\
               .sort_values(["creatorId", "epoch"])
    else:
        df = df.sort_values(["creatorId", "timestamp", "rssi"])
        df = df.groupby(['creatorId', 'epoch'], as_index=False)\
               .agg({"timestamp": "last", "bssid": "last", "rssi": "last"})
        
    return df

def get_filtered_data():
    '''
    Remove all participants who have returned less than p (ex.: 50%) of total possible battery records and
    filter locations to Saskatoon boundaries
    :return: the filtered data sets wifi and gps
    '''

    engine = create_engine("mysql+pymysql://" + user + ":" + pwd + "@" + server + ":" + port + "/" + database)

    s = "SELECT creatorId, timestamp, dutyCycleLevel, latitude, longitude " \
        "FROM location " \
        "WHERE location.latitude BETWEEN 52.058367 AND 52.214608  " \
        "AND location.longitude BETWEEN -106.7649138128 AND -106.52225318 " \
        "AND location.accuracy_meters <= 100 " \

    location = pd.read_sql(s, engine)

    s = "SELECT creatorId, timestamp, dutyCycleLevel, bssid, rssi " \
        "FROM wifi " \
        "WHERE wifi.rssi > -80"

    wifi = pd.read_sql(s, engine)

    #Find users with more than 50% of total battery records
    bat = pd.read_sql_table("battery", engine)
    bat = get_active_users(bat, 0.5)
    bat = bat["creatorId"].values

    #Only considers the users from the line before for location and wifi dataframes
    location = location[location["creatorId"].isin(bat)]
    wifi = wifi[wifi["creatorId"].isin(bat)]

    return location, wifi

def simplify_username(df):
    i = 0
    
    for user in np.array(pd.unique(df["creatorId"])):
        df.loc[(df['creatorId'] == user), 'creatorId'] = i
        i += 1
        
def convert_coord(df, is_utm):
    '''
    Convert gps to utm and vice-versa
    :param df: gps data frame
    :param utm: boolean indicating if it is converting to utm or not
    :return: gps data frame with the tables converted
    '''
    
    # UTM code for Saskatoon
    p = Proj(init='EPSG:32613')

    if is_utm:
        # Converts from latitude/longitudeg gps to UTM coordinates
        df['utmlongitude'], df['utmlatitude'] = p(df["longitude"].values, df["latitude"].values)
    else:
        # Converts from UTM coordinates to latitude/longitudeg gps
        df["longitude"], df["latitude"] = p(df["utmlongitude"].values, df["utmlatitude"].values, inverse=True)
    
    return

def get_gps_contacts(df, m):
    '''
    Stratify the data based on how close the participants are
    :param m: integer indicating the maximum distance to define "close"
    :param df: list with the contacts by duty cycle
    '''
    
    contacts = []
    dcs = pd.unique(df["epoch"])
    contact_dist = m**2
    
    for dc in dcs:
        dc_group = df[df['epoch'] == dc]
        users = pd.unique(dc_group["creatorId"])
        
        for i in range(0, len(users)):
            j = len(users) - 1
            dfUser = dc_group.loc[dc_group['creatorId'] == users[i]]

            while j > i:        
                dfUser2 = dc_group.loc[dc_group['creatorId']  == users[j]]
                latDist = ((dfUser['utmlatitude'].values - dfUser2['utmlatitude'])**2).values
                lonDist = ((dfUser['utmlongitude'].values - dfUser2['utmlongitude'])**2).values

                if((latDist + lonDist) <= contact_dist):
                    contacts.append((users[i], users[j], dc))
                    
                j = j - 1
                
    return contacts

def get_wifi_contacts(df, min_rssi):
    d = defaultdict(list)
    
    filtered_df = df[df['rssi'] >= min_rssi]
    filtered_df['dc_loc'] = list(zip(filtered_df['epoch'], filtered_df['bssid']))
    
    for idx, row in filtered_df.iterrows():
        d[row['dc_loc']].append(row['creatorId'])
    
    d = [{k:v} for k , v in sorted(d.items()) if len(v) > 1]
    
    #### convert the list[dict] to list[tuple] format
    formatted = []
    
    for row in d:
        for key, value in row.items():
            formatted.append((value[0], value[1], key[0]))

    return formatted
location, wifi = get_filtered_data()

print("Number of location records after filtering: " + str(len(location)))
print("Number of wifi records after filtering: " + str(len(wifi)))

simplify_username(location)
simplify_username(wifi)
location = agg_dc(location, True)
convert_coord(location, True)
gps_contacts_10 = get_gps_contacts(location, 10)
