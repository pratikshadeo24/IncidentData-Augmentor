# CIS6930SP24 - Assignment2

#### Name: Pratiksha Deodhar

## Description
<div style="text-align: justify">
Norman, Oklahoma police department regularly reports incidents, arrests, and other activities. In the assignment0 we extracted incidents and stored them in database. Now our goal is to further process the extracted information and generate augmented data such as "
Day of the Week", "Time of Day", "Weather", "Location Rank" etc. so that information can be used for end stream purposes.
</div>

## How to Install
### 1. Download pyenv:
```commandline
$ curl https://pyenv.run | bash
```
### 2. Install Python 3.11:
```commandline
$ pyenv install 3.11
```
### 3. Set it globally:
```commandline
$ pyenv global 3.11
```

### 4. Install required libraries
```commandline
$ pipenv install pypdf 
$ pipenv install pytest
$ pipenv install pytest-mock
$ pipenv install requests
```

## How to Run
```commandline
$ pipenv run python assignment2.py --urls <file_name.csv>
```

## How to Test
```commandline
$ pipenv run python -m pytest
```

## Demo
https://github.com/pratikshadeo24/cis6930sp24-assignment2/assets/30438714/b7827ee8-74b4-43b5-975b-8cdbe3448cda

## Code Description

### main
This function serves as the entry point of the script. It orchestrates the process of reading a file containing URLs, fetching incident data from each URL, extracting relevant incident details, and finally augmenting and printing the data.
It uses argparse to parse command-line arguments, requiring a file as an input (--urls), which it then passed to the main function.
- Function arguments
  - urls_filename (string) : The path to a text file containing a list of URLs. Each URL in this file points to a separate incident PDF from which data needs to be extracted.
- Return Value 
  - None. There is no return value, but this function leads to the generation of augmented incident data based on the input URLs.
  
### fetch_incidents
This function takes a URL as string and uses the `urllib.request` library to grab one incident pdf for the Norman Police Report Webpage.
- Function arguments: url (string)
- Return value: incident data from url in binary format

### extract_incidents
This function is designed to process binary data of a PDF document, extract text content from each page, and then 
compile the text into a structured format, presumably a list of incidents.
- Function arguments: incident data from `fetch_incidents` function
- Return value: list of incidents

### extract_page_text
This function is designed to extract text in the form of list of strings where each string represents a line of text 
extracted from the current page, with special considerations for the first and last pages of the document.
- Function arguments: 
  - page (PageObject)
  - page_num (int)
  - tot_pages (int)
- Return value: split_incidents (list of strings)

### split_all_incidents
This function is designed to process a block of text (page_text) and extract individual incidents from it
- Function arguments:
  - page_text: entire page content (list)
- Return value: incidents of particular page (list)

### refactor_page_data
This function processes a list of strings, each representing a line of text extracted from a PDF page, and transforms
this text to get data of incident's time, number, location, nature, ORI.
- Function arguments: page_text, (list of strings)
- Return value: page_incidents, (list of dictionaries) with all incident arguments

### extract_location_and_nature
This function is designed to parse a segment of text and separate it into two components: the location and the nature 
of an incident. This parsing is based on certain conditions related to the content and its format.
- Function arguments: record, which is a segment of individual record list
- Return value: 
  - loc_str: incident location (string)
  - nature_str: incident nature (string)

### augment_and_print_data
This function takes a list of incident records and augments each record with additional contextual information. It calculates and assigns location and incident ranks, determines if the EMS status is applicable, calculates geographic directions relative to a central point, and fetches corresponding weather conditions. Finally, it prints out the augmented incident data in a tab-separated format, suitable for further analysis or reporting.
- Function arguments 
  - incidents (list of dictionaries) : Each dictionary in this list represents an incident with its basic extracted data. The incidents are processed to augment additional information based on the given context and data available.
- Return value 
  - None. While the function doesn't return a value, it outputs to the console, printing the augmented incident data in a structured format.

### find_weather
This function is designed to retrieve weather conditions for a specific incident based on its geographic location and the time it occurred. It interacts with an external weather API to fetch historical weather data, enriching each incident record with environmental context that may be relevant for further analyses.
- Function arguments
  - incident (dictionary) : 
  - lat (float)
  - lon (float)
- Return value
  - weather_code (integer) : The function returns a weather code indicative of the specific weather conditions at the incident's location and time.

### get_lat_long
This function determines the geographical coordinates (latitude and longitude) of an incident based on its location description. It utilizes the Google Maps Geocoding API to convert location addresses or landmarks into precise geographic coordinates.
- Function arguments
  - incident (dictionary) : dictionary representing an individual incident
- Return value
  - (lat, lon) : geographic coordinates for the incident's location

### find_direction
This function calculates the cardinal direction of an incident location relative to a fixed central point, typically representing the center of a town or city. This computation helps in categorizing incidents based on their geographic orientation, which can be useful for spatial analysis, reporting, or further contextual understanding of the data.
- Function arguments
  - lat (float) : Latitude of the incident location.
  - lon (float) : Longitude of the incident location.
- Return value
  - direction (string) : cardinal direction of the incident location relative to the central point. Possible values include 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', or 'Unknown' if the input coordinates are invalid.

### calculate_location_ranks
This function assigns a rank to each unique incident location based on the frequency of incidents occurring at those locations. The function iterates through the list of incident records to aggregate the occurrences of each unique location. It then sorts these locations based on their frequency count, assigning ranks starting from the most frequent (rank 1) to the least frequent. In cases where multiple locations have the same frequency of incidents, they receive the same rank, following a dense ranking scheme.
- Function arguments
  - incidents (list of dictionaries) : Each dictionary in this list represents an incident, including a key for the incident location.
- Return value
  - location_ranks (dictionary) : mapping of each unique location to its rank based on incident frequency.

### calculate_incident_ranks
This function assigns a rank to each type of incident based on its frequency of occurrence across the dataset. The function iterates through the list of incident records to aggregate the occurrences of each unique nature. It then sorts these natures based on their frequency count, assigning ranks starting from the most frequent (rank 1) to the least frequent. In cases where multiple incidents have the same frequency of nature, they receive the same rank, following a dense ranking scheme.
- Function arguments
  - incidents (list of dictionaries) : Each dictionary represents an incident and includes information about the incident's nature.
- Return value
  - incident_ranks (dictionary) : mapping of each incident nature to its rank determined by frequency.

### check_ems_stat
This function determines whether an incident is associated with an EMS response. The function checks if the incident_ori for the current_incident directly indicates EMS involvement. If the initial check does not confirm EMS involvement, the function then examines a set range of incidents before and after the current incident. If any adjacent incident within this proximity window matches the EMS criteria (same time and location with an EMS indicator), the current incident is also classified as related to EMS.
- Function arguments
  - current_incident (dictionary) : The incident currently being evaluated, extracted from a broader list of incidents.
  - all_incidents (list of dictionaries) : The complete list of incidents, among which the function searches for proximal EMS-related incidents.
  - current_index (int) : The index of current_incident within all_incidents, used to locate temporally adjacent incidents.
- Return value
  - (lat, lon) : geographic coordinates for the incident's location
  - boolean value (1 or 0): The function returns 1 if the incident is related to EMS (either directly or through proximity association) and 0 otherwise.

### augment_incident
This function enriches each incident record with additional contextual and analytical data derived from its inherent attributes and external comparisons. Specifically, it assigns day of the week and time of day based on the incident's timestamp, and it incorporates location and incident ranks derived from broader dataset analyses.
- Function arguments
  - incident (dictionary) : The individual incident record to be augmented.
  - location_ranks (dictionary) : A precomputed mapping of locations to their respective ranks, based on the frequency of incidents occurring at each location.
  - incident_ranks (dictionary) : A precomputed mapping of incident types to their ranks, reflecting the relative commonality of each incident type within the dataset.
- Return value
  - None : The function does not return a value, it significantly modifies the incident dictionary in place, adding several new keys - "day_of_week", "time_of_day", "location_rank", "incident_rank".

### print_headers
This function is designed to output the column headers for a dataset that has been augmented with additional attributes.
- Function arguments
  - None : The function does not require any input parameters as it operates based on a predefined set of headers relevant to the augmented incident data structure.
- Return value
  - None : The function directly prints the headers to standard output.

### print_augmented_data
This function outputs the augmented data for a single incident record in a structured and readable format. This function is integral for presenting detailed incident information in a consistent, tab-separated layout, enabling effective data review and further processing.
- Function arguments
  - incident (dictionary) : A dictionary containing the augmented data for an individual incident.
- Return value
  - None : The function prints out a single line, representing the augmented incident data.

## Tests

### test_main 
- Purpose : This script tests the main function within the assignment2.main module, ensuring it correctly integrates and invokes the functionality within the assignment module, handling the workflow from URL fetching to data augmentation and printing.
- Tests : 
  - test_main : This test case mocks dependencies to simulate the main function's behavior, verifying the interaction between reading URLs, fetching incident data, extracting incidents, and augmenting data. It ensures that the fetch_incidents, extract_incidents, and augment_and_print_data functions are called the appropriate number of times and with the expected arguments.

### test_assignment.py
- Purpose : This script validates the logic and correctness of various functions in the assignment module, focusing on data processing, augmentation, and external API interaction.
- Tests : 
  - test_check_ems_stat : Validates the `check_ems_stat` function's ability to determine the correct EMS status based on the incident data and its context within adjacent incidents.
  - test_augment_incident : Ensures that the `augment_incident` function accurately calculates and assigns day of the week, time of day, location rank, and incident rank based on provided data.
  - test_calculate_location_ranks : Tests the `calculate_location_ranks` function to verify that it accurately calculates location ranks based on the frequency of incident occurrences at each location.
  - test_calculate_incident_ranks : Confirms that the `calculate_incident_ranks` function correctly assigns ranks to incident types based on their relative frequencies.
  - test_augment_and_print_data : Examines the `augment_and_print_data` function to ensure it correctly augments incident data and interacts properly with mocked dependencies for retrieving latitude/longitude and weather information.
  - test_find_direction : Checks the `find_direction` function to validate its directional calculation logic based on provided geographic coordinates.
  - test_find_weather : Verifies the interaction between the `find_weather` function and a mocked weather API, ensuring the correct weather code is determined for given incidents.
  - test_get_lat_long : Assesses the `get_lat_long` function, ensuring it interacts correctly with a mocked geocoding API to retrieve accurate geographic coordinates based on incident locations.

## Bugs and Assumptions
- There will be only 5 columns in the pdf and order of columns will be preserved. After splitting list, index 1 will give time, index 2 will give incident number, last index will give incident ori, rest index will be used to extract location and nature
- Page 0 of pdf will have a header and last page will have a footer which needs to be removed
- Location includes - float, decimal, uppercase and special characters( "/", ";"). "MVA", "COP", "EMS", "911", "9", "RAMPMVA", "HWYMotorist", "RAMPMotorist" are exceptions to this logic hence they are handled in each unique way
- Anything not included in location will be included in nature. Once we start writing into nature, nothing will be appended to location as location preceds nature column
- Incident number will always be of length 13, if it has more than that then we assume the extra text as initials of location
- Incident Date & Time, Incident number, and ORI will never be empty
- `geocoding` api does not offer any limitation for maximum number of requests per day, but there is a limitation of 3,000 QPM(Queries per minute)
- `Open Meteo` api used for finding weather is free for non-commercial use but there is a limitation of 10,000 requests per day
- If the `geocoding` api is not able to fetch lat long, the function `get_lat_lon` returns lat, long as None. The subsequent functions `find_weather` and `find_direction` called for None values of lat long return weather_code and site as "Unknown"
- In the `get_lat_long` function, there 1 additional check. When location by default has coordinates, it doesn't get passed to api, instead it is directly used for next function call. Also it has caching mechanism whereby if location is found in dictionary, it simply returns the stored lat long and api call is not required.
- Since the output is supposed to be printed in tab separated manner, so when any column values are not of same length, the next column indentation gets little skewed
