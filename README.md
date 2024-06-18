# Google Map Trip Planner

The utility filters places from Google Maps based on an query and exports them to a CSV file.

> Note: This script requires Python 3.6+
## How to run the script

- Install all dependencies with:

```
$ pip install -r requirements.txt
```

- Rename the file `secrets.ini.example` to `secrets.ini` and add the Google Maps API key.

## Usage

For fetching a list of attractions in Maharashtra, we can do:

```
$ python fetch.py --directory output/india/maharashtra --rating 4.5 --reviews 5000 --operator and --query "attractions in Maharashtra"
```

This will return all the attractions in Maharashtra that have a rating >= 4.5 *and* a review count >= 5000

### Excluding places from a query

Items can be excluded from a search query using the `--exclude` parameter.

```
$ python fetch.py --directory output/india/maharashtra --rating 4.5 --reviews 5000 --operator and --query "attractions in Maharashtra" --exclude park
```

More details can be viewed with the `--help` parameter:

```
$ python fetch.py --help

usage: fetch.py [-h] [--query QUERY] [--directory DIRECTORY] [--rating RATING]
                [--reviews REVIEWS] [--operator {and,or}]
                [--exclude {park,point_of_interest,establishment,museum,library,church,art_gallery,political} [{park,point_of_interest,establishment,museum,library,church,art_gallery,political} ...]]
                [--language {en,fr,de}] [--summary-length SUMMARY_LENGTH]

optional arguments:
  -h, --help            show this help message and exit
  --query QUERY         Search query for Google Maps API
  --directory DIRECTORY
                        Output directory
  --rating RATING       Minimum rating of the place(s)
  --reviews REVIEWS     Minimum review count of the place(s)
  --operator {and,or}   Operation to perform between ratings and reviews
                        count.
  --exclude {park,point_of_interest,establishment,museum,library,church,art_gallery,political} 
                        Exclude the places from the query result
  --language {en,fr,de}
                        Language of the Wikipedia link
  --summary-length SUMMARY_LENGTH
                        Limit the number of sentences in place summary.
```

## Using the generated CSV file
The CSV file generated can be used in Google My Maps to visualize all the places
