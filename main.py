import os
from math import sin, cos, sqrt, atan2, radians
import urllib.request
import json

"""
This program is designed to find the nearest park for whatever address/zipcode, etc, you enter
---------------------------------------------------------------------
I'm limiting myself to the Python's Standard Library for this personal project.
---------------------------------------------------------------------
Using Google Maps Platform API - https://developers.google.com/maps
---------------------------------------------------------------------
Geocoding API and Places API was used in the making of this program
---------------------------------------------------------------------
Quota Limit for both APIS:
Requests per minute per user: 10 
Requests per minute: 100
Requests per day: 1000
"""

#Use your own API KEY
api_key = "API KEY HERE"


def address_input():
    user_input = input("Enter an Address or Zip Code: ").replace(" ", "%20")
    return user_input



# JSON --> Python | Finds Info about user's location
def convert_user_location(address):
    parameters = "address=" + address
    key = "&key=" + api_key
    data_url = "https://maps.googleapis.com/maps/api/geocode/json?" + parameters + key
    content = urllib.request.urlopen(data_url).read().decode()
    data = json.loads(content)
    return data

# Finds Latitude and Longitude based on provided info
def get_user_location(map_data):
    location = {}
    for data in map_data["results"]:
        location["latitude_of_address"] = data['geometry']['location']['lat']
        location["longitude_of_address"] = data['geometry']['location']['lng']
    return location


# JSON --> Python | Finds info about Parks in the vivacity of the radius specified
def convert_park_location_data(location_data):
    location = "location=" + str(location_data["latitude_of_address"]) + "," + str(
        location_data["longitude_of_address"])
    radius = "&radius=" + str(2000)
    types = "&types=" + "park"
    key = "&key=" + api_key
    data_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?" + location + radius + types + key
    content = urllib.request.urlopen(data_url).read().decode()
    data = json.loads(content)
    return data


# Collects a variety of data for each park in the radius specified and returns that data in a single list.
def store_park_info(map_data):
    data_storage = []
    idiv_park_list = {}
    for data in map_data['results']:
        idiv_park_list['name_of_park'] = data['name']
        idiv_park_list['address_of_park'] = data['vicinity']
        idiv_park_list['latitude_of_park'] = data['geometry']['location']['lat']
        idiv_park_list['longitude_of_park'] = data['geometry']['location']['lng']
        if 'rating' in data:
            idiv_park_list['user_rating'] = data['rating']
        else:
            idiv_park_list['user_rating'] = "NOT AVAILABLE"
        if 'user_ratings_total' in data:
            idiv_park_list['user_ratings_total'] = data['user_ratings_total']
        else:
            idiv_park_list['user_ratings_total'] = "NOT AVAILABLE"
        data_storage.append(idiv_park_list.copy())
    return data_storage


# Finds the distance in miles from the address provided to the park using the Haversine formula
def calculate_distance_to_park(address_geocode, park_geocode):
    latitude_of_address = radians(address_geocode['latitude_of_address'])
    longitude_of_address = radians(address_geocode['longitude_of_address'])
    latitude_of_park = radians(park_geocode['latitude_of_park'])
    longitude_of_park = radians(park_geocode['longitude_of_park'])
    latitude_distance = latitude_of_park - latitude_of_address
    longitude_distance = longitude_of_park - longitude_of_address
    initial_calculation = sin(latitude_distance / 2) ** 2 + cos(latitude_of_address) * cos(latitude_of_park) \
                          * sin(longitude_distance / 2) ** 2
    final_calculation = 2 * atan2(sqrt(initial_calculation), sqrt(1 - initial_calculation))
    # Radius of Earth in Miles
    radius_of_earth = 3958.761
    distance = radius_of_earth * final_calculation
    return distance


# Calculates the amount of miles the user is from the nearest park and then sorts it from least to most miles
def store_more_data():
    address = address_input()
    convert_address = convert_user_location(address)
    geocode_address = get_user_location(convert_address)
    convert_park_data = convert_park_location_data(geocode_address)
    data = store_park_info(convert_park_data)
    for each_dict in data:
        distance_in_miles = calculate_distance_to_park(geocode_address, each_dict)
        each_dict['miles'] = distance_in_miles
    data.sort(key=lambda x: x['miles'])
    return data


# Displays to the user the nearest park with some extra info provided
def display_data():
    data = store_more_data()
    print("Here's a list of parks you can visit nearby: \n")
    for counter, each_dict in enumerate(data):
        print(f"{str(counter + 1)}. {each_dict['name_of_park']} is located at {each_dict['address_of_park']} "
              f"and is approximately {str(round(each_dict['miles'], 2))} "
              f"miles away with a user rating of {str(each_dict['user_rating'])} by "
              f"{str(each_dict['user_ratings_total'])} user(s)\n")


def main():
    display_data()


if __name__ == '__main__':
    main()
