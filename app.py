import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

st.set_page_config(layout="wide")  # Set wide layout for better visualization
st.title("Disaster Reporting Map")

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "address" not in st.session_state:
    st.session_state.address = ""

def get_coordinates(address):
    # Initialize the Google Maps API client
    gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

    # geocoding an address
    geocode_result = gmaps.geocode(address)

    # extract latitude and longitude from the first result
    location = geocode_result[0].get("geometry", {}).get("location", {})
    lat = location.get("lat")
    lon = location.get("lng")

    if lat is not None and lon is not None:
        return lat, lon
    else:
        print("Could not extract latitude and longitude.")
        return None, None

def get_disaster_pins():
    # TODO: send request call to flask app to get disaster data
    # send dummy dataframe for now from csv file
    
    # check if the file exists if not send dummy data
    if not os.path.exists("disasters.csv"):
        return pd.DataFrame({
            "latitude": [37.77, 37.78, 37.79],
            "longitude": [-122.41, -122.42, -122.43],
            "description": ["Earthquake", "Flood", "Fire"]
        })
    else:
        data = pd.read_csv("disasters.csv")
        data["latitude"] = data["latitude"].astype(float)
        data["longitude"] = data["longitude"].astype(float)
        data["description"] = data["description"].astype(str)

        return data
    """
    return pd.DataFrame({
        "latitude": [37.77, 37.78, 37.79],
        "longitude": [-122.41, -122.42, -122.43],
        "description": ["Earthquake", "Flood", "Fire"]
    })
    """

# Sidebar form for input
with st.sidebar.form("input_form"):
    st.header("Enter Your Location")
    address = st.text_input("Address", placeholder="Enter an address...")
    radius = st.slider("Search Radius (km)", min_value=1, max_value=50, value=10)
    
    #submitted = st.form_submit_button("Submit")
    if st.form_submit_button("Submit"):
        st.session_state.submitted = True
        st.session_state.address = address

# Display map
if st.session_state.submitted and st.session_state.address.strip():
    lat, lon = get_coordinates(st.session_state.address)
    
    if lat is not None and lon is not None:
        st.write(f"Coordinates for '{address}': Latitude: {lat}, Longitude: {lon}")
        
        # center the map on the input coordinates
        map_center = [lat, lon]
        folium_map = folium.Map(location=map_center, zoom_start=12)

        # add a marker for the input location
        folium.Marker([lat, lon], popup=f"Location: {address}").add_to(folium_map)

        # add disaster pins to map
        disaster_pins = get_disaster_pins()
        for index, row in disaster_pins.iterrows():
            folium.Marker([row["latitude"], row["longitude"]], popup=row["description"]).add_to(folium_map)

        # highlight radius
        folium.Circle(
            location=map_center,
            radius=radius * 1000,  # Convert km to meters
            color="blue",
            fill=True,
            fill_opacity=0.1,
        ).add_to(folium_map)

        # display map 
        st_folium(folium_map, width=700, height=500)
        
    else:
        st.error("Unable to fetch coordinates. Please try again.")
else:
    st.info("Enter an address in the sidebar to get started.")

    