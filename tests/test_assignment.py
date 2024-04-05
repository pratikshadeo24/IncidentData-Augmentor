import pytest
from assignment2 import assignment


@pytest.fixture
def sample_incidents():
    return [
        {'incident_location': '1880 CLASSEN BLVD',
         'incident_nature': 'Traffic Stop',
         'incident_number': '2024-00013477',
         'incident_ori': 'EMSSTAT',
         'incident_time': '2/25/2024 0:04'
         },
        {'incident_location': '2120 W BROOKS ST',
         'incident_nature': 'Mutual Aid',
         'incident_number': '2024-00013489',
         'incident_ori': 'OK0140200',
         'incident_time': '2/25/2024 0:06'
         },
        {'incident_location': '1880 CLASSEN BLVD',
         'incident_nature': 'Traffic Stop',
         'incident_number': '2024-00013479',
         'incident_ori': 'OK0140200',
         'incident_time': '2/25/2024 0:08'
         }
    ]


@pytest.fixture
def weather_resp_json():
    return {
        'latitude': 35.184532,
        'longitude': -97.46173,
        'generationtime_ms': 0.21600723266601562,
        'utc_offset_seconds': 0, 'timezone': 'GMT',
        'timezone_abbreviation': 'GMT', 'elevation': 348.0,
        'hourly': {'weather_code': [0, 1, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
    }


@pytest.mark.parametrize("current_incident, current_index, expected", [
    ({'incident_ori': 'EMSSTAT'}, 1, 1),
    ({'incident_ori': 'OK0140200', 'incident_time': '2/25/2024 0:04', 'incident_location': '1880 CLASSEN BLVD'}, 2, 1),
    ({'incident_ori': 'OK0140200', 'incident_time': '2/20/2024 0:04'}, 2, 0)
])
def test_check_ems_stat(sample_incidents, current_incident, current_index, expected):
    # Execute
    actual_val = assignment.check_ems_stat(current_incident, sample_incidents, current_index)

    # Assert
    assert actual_val == expected


def test_augment_incident():
    incident = {'incident_location': '1880 CLASSEN BLVD',
                'incident_nature': 'Traffic Stop',
                'incident_number': '2024-00013477',
                'incident_ori': 'OK0140200',
                'incident_time': '2/25/2024 0:04'}
    location_rank = {'1880 CLASSEN BLVD': 1, '2120 W BROOKS ST': 2}
    incident_rank = {'Mutual Aid': 2, 'Traffic Stop': 1}

    # Execute
    assignment.augment_incident(incident, location_rank, incident_rank)

    # Asserts
    assert incident['day_of_week'] == 7
    assert incident['time_of_day'] == 0
    assert incident['location_rank'] == 1
    assert incident['incident_rank'] == 1


def test_calculate_location_ranks(sample_incidents):
    # Execute
    actual_loc_ranks = assignment.calculate_location_ranks(sample_incidents)

    # Expect
    expected_loc_ranks = {'1880 CLASSEN BLVD': 1, '2120 W BROOKS ST': 2}

    # Asserts
    assert actual_loc_ranks['1880 CLASSEN BLVD'] == expected_loc_ranks['1880 CLASSEN BLVD']
    assert actual_loc_ranks['2120 W BROOKS ST'] == expected_loc_ranks['2120 W BROOKS ST']


def test_calculate_incident_ranks(sample_incidents):
    # Execute
    actual_loc_ranks = assignment.calculate_incident_ranks(sample_incidents)

    # Expect
    expected_loc_ranks = {'Mutual Aid': 2, 'Traffic Stop': 1}

    # Asserts
    assert actual_loc_ranks['Mutual Aid'] == expected_loc_ranks['Mutual Aid']
    assert actual_loc_ranks['Traffic Stop'] == expected_loc_ranks['Traffic Stop']


def test_augment_and_print_data(mocker, sample_incidents):
    # Mocks
    mocker.patch('assignment2.assignment.get_lat_long',
                 return_value=(35.20458136231884, -97.43226908695652))
    mocker.patch('assignment2.assignment.find_weather', return_value=0)

    # Execute
    actual_aug_incidents = assignment.augment_and_print_data(sample_incidents)

    # Expected
    expected_aug_incidents = [
        {'incident_location': '1880 CLASSEN BLVD',
         'incident_nature': 'Traffic Stop',
         'incident_number': '2024-00013477',
         'incident_ori': 'OK0140200',
         'incident_time': '2/25/2024 0:04',
         'day_of_week': 7,
         'time_of_day': 0,
         'location_rank': 1,
         'incident_rank': 1,
         'ems_stat': 0,
         'side_of_town': 'SE',
         'weather': 0
         },
        {'incident_location': '2120 W BROOKS ST',
         'incident_nature': 'Mutual Aid',
         'incident_number': '2024-00013489',
         'incident_ori': 'OK0140200',
         'incident_time': '2/25/2024 0:06',
         'day_of_week': 7, 'time_of_day': 0,
         'location_rank': 2, 'incident_rank': 2,
         'ems_stat': 0, 'side_of_town': 'SE', 'weather': 0
         },
        {'incident_location': '1880 CLASSEN BLVD',
         'incident_nature': 'Traffic Stop',
         'incident_number': '2024-00013479',
         'incident_ori': 'OK0140200',
         'incident_time': '2/25/2024 0:08',
         'day_of_week': 7, 'time_of_day': 0,
         'location_rank': 1, 'incident_rank': 1,
         'ems_stat': 0, 'side_of_town': 'SE', 'weather': 0
         }
    ]

    # Asserts
    actual_aug_incidents[0]['location_rank'] = expected_aug_incidents[0]['location_rank']
    actual_aug_incidents[1]['location_rank'] = expected_aug_incidents[1]['location_rank']
    actual_aug_incidents[2]['location_rank'] = expected_aug_incidents[2]['location_rank']
    actual_aug_incidents[0]['incident_rank'] = expected_aug_incidents[0]['incident_rank']
    actual_aug_incidents[1]['incident_rank'] = expected_aug_incidents[1]['incident_rank']
    actual_aug_incidents[2]['incident_rank'] = expected_aug_incidents[2]['incident_rank']


@pytest.mark.parametrize("lat, lon, expected", [
    (35.20458136231884, -97.43226908695652, 'SE'),
    (35.251261, -97.416448, 'NE'),
    (35.207455, -97.472611, 'SW')
])
def test_find_direction(lat, lon, expected):
    # Execute
    actual_direction = assignment.find_direction(lat, lon)

    # Asserts
    assert actual_direction == expected


@pytest.mark.parametrize("incident, lat, lon, expected", [
    ({'incident_time': '2/25/2024 0:04'}, 35.20458136231884, -97.43226908695652, 0),
    ({'incident_time': '2/25/2024 1:06'}, 35.207455, -97.472611, 1),
    ({'incident_time': '2/25/2024 4:08'}, 35.189401448979595, -97.45121940816327, 5)
])
def test_find_weather(mocker, weather_resp_json, incident, lat, lon, expected):
    # Mocks
    mock_spi_resp = mocker.Mock()
    mock_spi_resp.json.return_value = weather_resp_json
    mocker.patch('assignment2.assignment.requests.get', return_value=mock_spi_resp)

    # Execute
    actual_weather_code = assignment.find_weather(incident, lat, lon)

    # Assert
    assert actual_weather_code == expected


@pytest.mark.parametrize("incident, loc_resp_json, expected", [
    ({'incident_location': '1062 W BOYD ST'},
     {'results': [{'formatted_address': '1062 W Boyd St, Norman, OK 73069, USA', 'place_id': 'EiUxMDYyIFcgQ',
                   'types': ['street_address'], 'geometry': {'location': {'lat': 35.2109587, 'lng': -97.4587691}}}]},
     (35.2109587, -97.4587691)),
    ({'incident_location': 'TELLURIDE LN / CLASSEN BLVD'},
     {'results': [{'formatted_address': 'Classen Blvd & Telluride Ln, Norman, OK 73071, USA', 'place_id': 'EiUxMDYyIgQ',
                   'types': ['intersection'], 'geometry': {'location': {'lat': 35.1942994, 'lng': -97.42392339999999}}}]},
     (35.1942994, -97.42392339999999)),
    ({'incident_location': '35.189401448979595, -97.45121940816327'},
     {'results': [{'county': 'Cleveland County', 'street': 'West Imhoff Road', 'housenumber': '750',
                   'lon': -97.45121940816327, 'lat': 35.189401448979595}]},
     (35.189401448979595, -97.45121940816327))
])
def test_get_lat_long(mocker, incident, loc_resp_json, expected):
    # Mocks
    mock_spi_resp = mocker.Mock()
    mock_spi_resp.json.return_value = loc_resp_json
    mocker.patch('assignment2.assignment.requests.get', return_value=mock_spi_resp)

    # Execute
    actual_weather_code = assignment.get_lat_long(incident)

    # Assert
    assert actual_weather_code[0] == expected[0]
    assert actual_weather_code[1] == expected[1]







