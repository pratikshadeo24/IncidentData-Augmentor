import argparse
from assignment2 import assignment

def main(urls_filename):

    with open(urls_filename, 'r') as file:
        urls = file.read().splitlines()

    all_incidents = []

    for url in urls:
        # get incident PDF data
        incident_data = assignment.fetch_incidents(url)

        # extract incident data
        incidents = assignment.extract_incidents(incident_data)

        all_incidents.extend(incidents)

    augmented_incidents = assignment.augment_and_print_data(all_incidents)


if __name__ == "__main__":
    # initialize command-line argument parsing
    parser = argparse.ArgumentParser()
    # define the required command-line argument '--urls' for the incident summary URL
    parser.add_argument(
        "--urls", type=str, required=True, help="File containing list of incident URLs."
    )
    # parse command-line arguments
    args = parser.parse_args()
    if args.urls:
        main(args.urls)