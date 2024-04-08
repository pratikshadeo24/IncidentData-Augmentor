import pytest
from assignment2 import main


@pytest.fixture
def mock_urls():
    # This simulates the content of the URLs file
    return ["http://testurl1.com", "http://testurl2.com"]


def test_main(mocker, mock_urls):
    # Mocks
    mocker.patch('builtins.open', mocker.mock_open(read_data='\n'.join(mock_urls)))
    fetch_incidents_mock = mocker.patch("functions.fetch_incidents", return_value="PDF data")
    extract_incidents_mock = mocker.patch("functions.extract_incidents", return_value=[{'incident_data': 'data'}])
    # create_json_mock = mocker.patch("functions.create_json")
    augment_data_mock = mocker.patch("functions.augment_and_print_data", return_value=[{'augmented_data': 'data'}])
    # print_augmented_data_mock = mocker.patch("functions.print_augmented_data")

    # Path to the file containing URLs
    urls_filename = "urls.txt"
    # Execute the main function with the mocked URLs file
    main(urls_filename)

    # Assert that each mocked function was called the correct number of times
    assert fetch_incidents_mock.call_count == len(mock_urls)
    assert extract_incidents_mock.call_count == len(mock_urls)
    # Augment and print functions should only be called once since they are called after aggregating all incidents
    augment_data_mock.assert_called_once()
    # print_augmented_data_mock.assert_called_once()