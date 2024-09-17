import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()

google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')

map_client = googlemaps.Client(key=google_maps_api_key)


def get_current_location(location):
    # Initialize Google Maps client

    # Geocode the location
    geocode_result = map_client.geocode(location)

    if geocode_result:
        # Extract latitude and longitude from the geocode result
        geometry = geocode_result[0]['geometry']['location']
        latitude = geometry['lat']
        longitude = geometry['lng']
        return latitude, longitude
    else:
        return None, None


def find_nearest_hospitals(user_location):
    lat, long = get_current_location(user_location)
    loc = (lat, long)
    print(loc)
    hospitals = map_client.places_nearby(location=loc,
                                    radius=5000,
                                    type='hospital',
                                    keyword='spital')

    if hospitals['status'] == 'OK' and hospitals['results']:
        # Extract relevant information for each hospital
        nearest_hospitals = []
        for hospital in hospitals['results']:
            print(hospital)
            name = hospital['name']
            address = hospital['vicinity']
            location = hospital['geometry']['location']
            # Calculate distance (optional)
            distance = map_client.distance_matrix(loc, location)['rows'][0]['elements'][0]['distance']['text']
            nearest_hospitals.append({'name': name, 'address': address, 'location': location, 'distance': distance})

        nearest_hospitals.sort(key=lambda x: float(x['distance'].split()[0]))
        return nearest_hospitals, loc
    else:
        return None

def reverse_geocode(latitude, longitude):
    reverse_geocode_result = map_client.reverse_geocode((latitude, longitude))
    print()
    print(reverse_geocode_result)
    return reverse_geocode_result[0].get('formatted_address')

def find_nearest_hospitals_current_location(latitude, longitude):
    loc = (latitude, longitude)
    print(loc)
    hospitals = map_client.places_nearby(location=loc,
                                    radius=5000,
                                    type='hospital',
                                    keyword='spital')

    if hospitals['status'] == 'OK' and hospitals['results']:
        # Extract relevant information for each hospital
        nearest_hospitals = []
        for hospital in hospitals['results']:
            print(hospital)
            name = hospital['name']
            address = hospital['vicinity']
            location = hospital['geometry']['location']
            # Calculate distance (optional)
            distance = map_client.distance_matrix(loc, location)['rows'][0]['elements'][0]['distance']['text']
            nearest_hospitals.append({'name': name, 'address': address, 'location': location, 'distance': distance})

        nearest_hospitals.sort(key=lambda x: float(x['distance'].split()[0]))
        return nearest_hospitals, loc
    else:
        return None


if __name__ == "__main__":
    location = "Str. Seliste nr. 16, alba iulia"
    current_location = get_current_location(location)
    print(current_location)
    hospitals, loc = find_nearest_hospitals(location)
    print(hospitals)
    location_to_adress = reverse_geocode(46.0679819869329, 23.554844507866925)
    print(f"Reversed location: {location_to_adress}")
    hospitals, loc = find_nearest_hospitals_current_location(46.0679819869329, 23.554844507866925)
    print(hospitals)