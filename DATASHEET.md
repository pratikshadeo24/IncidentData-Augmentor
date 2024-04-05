# Datasheet for dataset "Augmented Police Department Incident Records"

## Motivation

1. For what purpose was the dataset created?
- The dataset was created to collect augmented data extracted from public police department records, enhancing its utility for analysis with additional context like Day of the Week, Time of Day, Weather, Location Rank, Side of Town, Incident Rank, Nature, and EMSSTAT.
Composition

2. Who created the dataset (e.g., which team, research group) and on behalf of which entity (e.g., company, institution, organization)?
- This particular augmented dataset was created as an individual class assignment. There was no entity directly involved in it.

## Composition

1. What do the instances that comprise the dataset represent?
- Each instance represents an augmented incident data from the police department, each record comprise Day of the Week, Time of Day, Weather, Location Rank, Side of Town, Incident Rank, Nature, and EMSSTAT.

2. How many instances are there in total?
- The total count would depend on the number of incidents processed during the augmentation; this should match the number of incident records in the input data. As per the problem statement, no of incidents depend on the no. of urls provided in the csv input file.

3. What data does each instance consist of?
- An instance comprises incident Day of the Week, Time of Day, Weather, Location Rank, Side of Town, Incident Rank, Nature, and EMSSTAT.

4. Is the dataset self-contained, or does it link to or otherwise rely on external resources (e.g., websites, tweets, other datasets)?
- This augmented data relies on the public Norman police department records. Augmented data size will depend on the no .of incidents present in the urls contained in csv file.

## Collection Process

1. How was the data associated with each instance acquired?
- Data was programmatically extracted from the provided public Norman Police Department incidents as urls in csv file. Some data was easily extracted by building programmatic logic and others such as site of town and weather required use of external apis.

## Preprocessing/cleaning/labeling

1. Was any preprocessing/cleaning/labeling of the data done?
- The original incident data underwent augmentation, including weather lookup, time and location parsing, and rank assignments. No explicit labeling was mentioned beyond inherent data features.

2. Was the “raw” data saved in addition to the preprocessed/cleaned/labeled data (e.g., to support unanticipated future uses)?
- Raw data from Normal Police Department passed as incident urls is not saved but the intermediate results are extracted as dictionary on which further augmentation took place to produce the augmented data.

## Uses

1. Has the dataset been used for any tasks already?
- Ideally, this dataset is intended for analysis and could be used in various tasks like trend analysis, pattern recognition, or as input for further machine learning models.

2. What (other) tasks could the dataset be used for?
- Besides the tasks mentioned above, it could assist in resource allocation, policy making, or criminology studies.

## Distribution

1. How will the dataset be distributed?
- This would depend on the dissemination strategy. It could be distributed through an institutional repository, on a website, or via direct requests.

## Maintenance

1. Who is supporting/hosting/maintaining the dataset?
- Since currently it's a part of class assignment, nobody is hosting it. It's simply printed to the stdout.