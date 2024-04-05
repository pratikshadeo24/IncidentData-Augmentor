import io
import re
import urllib.request
from pypdf import PdfReader
from datetime import datetime
from collections import Counter
import math
import requests
from requests.structures import CaseInsensitiveDict

lat_long_dict = {}


def fetch_incidents(url):
    """Download PDF data from provided URL

    Params:
        url (str): API to download PDF Document
    Return:
        data (bytes): Data of the PDF Document
    """
    try:
        # define a dictionary of HTTP headers to simulate a request from a web browser
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 "
                          "Safari/537.17"
        }
        # make an HTTP GET request to the specified URL with the headers
        data = urllib.request.urlopen(
            urllib.request.Request(url, headers=headers)
        ).read()
        # return the content of the HTTP response
        return data
    except Exception as ex:
        print("ERROR in fetching incidents: ", ex)


def extract_incidents(incident_data):
    """Extracts and gather incidents from PDF Document page-wise

    Params:
        incident_data (bytes): PDF document data
    Return:
        incidents (list): All incidents with extracted fields
    """
    # convert download data to bytes object
    pdf_buffer = io.BytesIO(incident_data)
    # create PDFReader object
    reader = PdfReader(pdf_buffer)
    # get total number of pages
    tot_pages = len(reader.pages)

    incidents = []
    for page_num in range(tot_pages):
        # create specific page object
        page = reader.pages[page_num]
        # extract text
        page_text = extract_page_text(page, page_num, tot_pages)
        # refactor page text to capture different fields of incident
        incidents.extend(refactor_page_data(page_text))

    # create_json(incidents)
    return incidents


def extract_page_text(page, page_num, tot_pages):
    """Extract page text based on the page number.

    Params:
    - page (PageObject): specific page object
    - page_num (int): current page number
    - tot_pages (int): total number of pages in PDF document
    Return:
         split_incidents (List[str]): Extracted incidents
    """
    if page_num == 0:
        # extract the page text and remove header and column heading
        page_text = page.extract_text()[57:-55]
        # split the page text into individual incidents
        split_incidents = split_all_incidents(page_text)
    elif page_num == tot_pages - 1:
        # extract the page text
        page_text = page.extract_text()
        # split the page text into individual incidents
        split_incidents = split_all_incidents(page_text, 'last')
    else:
        # extract the page text
        page_text = page.extract_text()
        # split the page text into individual incidents
        split_incidents = split_all_incidents(page_text)

    # return incidents of a single page
    return split_incidents


def split_all_incidents(page_text, page_type=None):
    """Splits each incident based on date.

    Params:
    - page_text (str): page content
    - page_type (str/None): type of page, could be 'last' or 'None'
    Return:
         extracted_incident (list): Extract incidents
    """
    # regex for recognizing date
    pattern = r'(?=\d{1,2}/\d{1,2}/\d{4})'
    # split the page text into list of incidents using date regex
    extracted_incidents = re.split(pattern, page_text.strip())
    if page_type == 'last':
        # remove the footer from last page
        extracted_incidents = extracted_incidents[:-1]
    # filter out any empty strings
    extracted_incidents = [incident for incident in extracted_incidents if incident]

    # return extracted incidents
    return extracted_incidents


def refactor_page_data(page_text):
    """Filter specific fields from the page content.

    Params:
        page_text (list): extracted incidents
    Return:
        page_incidents (List): List of extracted fields of each incident
    """
    page_incidents = []
    for i in range(len(page_text)):
        # split individual incidents into tokens to extract fixed fields
        record = page_text[i].split()
        rec_time = record[0] + " " + record[1]
        rec_incident_num = record[2]
        rec_incident_ori = record[-1]

        if record[3: len(record)-1]:
            # extract location and nature
            location, nature = extract_location_and_nature(record[3: len(record)-1])
        else:
            location, nature = "", ""
        # handle edge case when extra text incident number has an extra text
        if len(rec_incident_num) > 13:
            location = rec_incident_num[13:] + ' ' + location
            rec_incident_num = rec_incident_num[:13]

        # collect each incident record
        page_incidents.append(
            {
                "incident_time": rec_time,
                "incident_number": rec_incident_num,
                "incident_location": location,
                "incident_nature": nature,
                "incident_ori": rec_incident_ori,
            }
        )

    # return extracted fields of all the incidents of a specific page
    return page_incidents


def extract_location_and_nature(record):
    """Extract location and nature of an incident.

    Params:
        record (list): segment of an incident
    Return:
    - loc_str (str): Location of an incident
    - nature_str (str): Nature of an incident
    Raise:
        Exception while modifying location and nature for an edge case
    """
    location, nature = [], []
    for rec in record:
        # handle location and nature edge cases
        if len(nature) == 0 and rec != "MVA" and rec != "COP" and rec != "EMS" and rec != "RAMPMVA" and (
                rec.isdecimal() or rec.isupper() or rec == "/" or ';' in rec or rec == '1/2'):
            location.append(rec)
        elif rec == 'HWYMotorist' or rec == 'RAMPMotorist':
            location.append(rec.split('Motorist')[0])
            nature.append('Motorist')
        elif rec == "RAMPMVA":
            location.append('RAMP')
            nature.append('MVA')
        else:
            nature.append(rec)

    try:
        if location:
            # handle edge case when location ends with numeric
            if location[-1].isnumeric() and len(location[-1]) != 1:
                nature.insert(0, location[-1])
                location.pop()
    except Exception as ex:
        print("ERROR in Location: ", ex)

    # convert location and nature into string
    loc_str = " ".join(location)
    nature_str = " ".join(nature)

    return loc_str, nature_str


def augment_and_print_data(incidents):
    # Pre-calculate location and incident ranks
    location_ranks = calculate_location_ranks(incidents)
    incident_ranks = calculate_incident_ranks(incidents)

    # Augment each incident with additional data including EMSSTAT
    for i, incident in enumerate(incidents):
        augment_incident(incident, location_ranks, incident_ranks)
        incident['ems_stat'] = check_ems_stat(incident, incidents, i)
        lat, lon = get_lat_long(incident)
        incident['side_of_town'] = find_direction(lat, lon)
        incident['weather'] = find_weather(incident, lat, lon)
        if i == 0:
            print_headers()
        print_augmented_data(incident)
    return incidents


def find_weather(incident, lat, lon):
    # If latitude or longitude is None, return "Unknown" for the weather
    if lat is None or lon is None:
        return "Unknown"

    url = "https://archive-api.open-meteo.com/v1/archive"

    date_time = datetime.strptime(incident['incident_time'], "%m/%d/%Y %H:%M")
    date = date_time.date()
    hour = date_time.hour

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date,
        "end_date": date,
        "hourly": "weather_code"
    }

    resp = requests.get(url, params=params)
    resp = resp.json()
    weather_code = resp['hourly']['weather_code'][hour]
    return weather_code


def get_lat_long(incident):

    # Google Maps Geocoding API endpoint
    url = "https://maps.googleapis.com/maps/api/geocode/json"

    loc = incident.get('incident_location')

    if loc in lat_long_dict:
        return lat_long_dict[loc]

    else:
        # Check if the location is already in coordinate format
        pattern = r'^-?\d{1,2}(?:\.\d+)?, ?-?\d{1,3}(?:\.\d+)?$'
        if bool(re.match(pattern, loc)):
            lat, lon = loc.split(",")
            return float(lat), float(lon)

        # Prepare the parameters for the API request
        params = {
            "address": loc,
            "key": "AIzaSyBijnKeE7jVUe-xzt2lOiHff5Dv-cyhYy0"  # Replace with your actual API key
        }

        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"

        # Make the request to the Google Maps API
        resp = requests.get(url, headers=headers, params=params)
        resp = resp.json()

        try:
            # Extract the latitude and longitude from the API response
            results = resp['results'][0]['geometry']['location']
            lat, lon = results['lat'], results['lng']
        except (IndexError, KeyError, Exception) as e:
            lat, lon = None, None
        lat_long_dict[loc] = (lat, lon)
        return lat, lon


def find_direction(lat, lon):
    # If latitude or longitude is None, return "Unknown" for the direction
    if lat is None or lon is None:
        return "Unknown"

    # Coordinates for the center of the town
    center_latitude = 35.220833
    center_longitude = -97.443611

    # Convert all latitudes and longitudes from degrees to radians
    center_lat_rad, center_lon_rad = map(math.radians, [center_latitude, center_longitude])
    target_lat_rad, target_lon_rad = map(math.radians, [lat, lon])

    # Calculate the differences in coordinates
    delta_lon = target_lon_rad - center_lon_rad
    delta_lat = target_lat_rad - center_lat_rad

    # Calculate the angle/bearing from the center of the town to the target location
    x = math.sin(delta_lon) * math.cos(target_lat_rad)
    y = math.cos(center_lat_rad) * math.sin(target_lat_rad) - (
            math.sin(center_lat_rad) * math.cos(target_lat_rad) * math.cos(delta_lon))
    bearing = (math.degrees(math.atan2(x, y)) + 360) % 360

    # Define the eight cardinal and intercardinal directions
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

    # Determine the direction based on the bearing
    direction_idx = int((bearing + 22.5) // 45) % 8
    return directions[direction_idx]


def calculate_location_ranks(incidents):
    # Calculate and return location ranks
    locations = [incident['incident_location'] for incident in incidents]
    location_counts = Counter(locations)
    ranked_locations = sorted(location_counts.items(), key=lambda x: (-x[1], x[0]))

    location_ranks = {}
    current_rank = 0
    last_count = None
    for i, (location, count) in enumerate(ranked_locations, start=1):
        if count != last_count:
            current_rank = i
        location_ranks[location] = current_rank
        last_count = count

    return location_ranks


def calculate_incident_ranks(incidents):
    # Calculate and return incident ranks based on incident nature
    natures = [incident['incident_nature'] for incident in incidents]
    nature_counts = Counter(natures)
    ranked_natures = sorted(nature_counts.items(), key=lambda x: (-x[1], x[0]))

    incident_ranks = {}
    current_rank = 0
    last_count = None
    for i, (nature, count) in enumerate(ranked_natures, start=1):
        if count != last_count:
            current_rank = i
        incident_ranks[nature] = current_rank
        last_count = count

    return incident_ranks


def check_ems_stat(current_incident, all_incidents, current_index):
    # Check current incident's ORI
    if current_incident['incident_ori'].upper() == 'EMSSTAT':
        return 1

    window = 3
    start_index = max(0, current_index - window)
    end_index = min(len(all_incidents), current_index + window + 1)

    # Check the previous and subsequent records for shared time and location with EMSSTAT
    for i in range(start_index, end_index):
        if i != current_index:  # Skip the current incident since it will be checked separately
            other_incident = all_incidents[i]
            if (other_incident['incident_ori'].upper() == 'EMSSTAT' and
                    other_incident['incident_time'] == current_incident['incident_time'] and
                    other_incident['incident_location'] == current_incident['incident_location']):
                return 1
    return 0


def augment_incident(incident, location_ranks, incident_ranks):
    # Augmenting the incident with location rank, incident rank, etc.
    incident_datetime_str = incident.get("incident_time", "1/1/1900 00:00")
    incident_datetime = datetime.strptime(incident_datetime_str, "%m/%d/%Y %H:%M")

    incident['day_of_week'] = incident_datetime.isoweekday()
    incident['time_of_day'] = incident_datetime.hour
    incident['location_rank'] = location_ranks.get(incident['incident_location'], -1)
    incident['incident_rank'] = incident_ranks.get(incident['incident_nature'], -1)


def print_headers():
    headers = [
        "Day of the Week", "Time of Day", "Weather",
        "Location Rank", "Side of Town", "Incident Rank",
        "Nature", "EMSSTAT"
    ]
    print("\t".join(headers))


def print_augmented_data(incident):

    day_of_week = incident.get('day_of_week')
    time_of_day = incident.get('time_of_day')
    location_rank = incident.get('location_rank')
    incident_rank = incident.get('incident_rank')
    incident_nature = incident.get('incident_nature')
    ems_stat = incident.get('ems_stat')
    side_of_town = incident.get('side_of_town')
    weather = incident.get('weather')

    print(f"{day_of_week}\t{time_of_day}\t{weather}\t{location_rank}\t{side_of_town}\t{incident_rank}\t{incident_nature}\t{ems_stat}")