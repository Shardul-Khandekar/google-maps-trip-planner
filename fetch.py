import csv
import json
import pathlib
import operator
import requests
import argparse
import configparser

import wikipedia

config = configparser.ConfigParser()
config.read('secrets.ini')

GMAPS_API_KEY = config['API_KEYS']['GOOGLE_MAPS']
PLACE_CATEGORIES = ['park', 'point_of_interest', 'establishment', 'museum', 'library', 'church', 'art_gallery', 'political']
# Search query operators.
LOGICAL_OPERATORS = {
    'and': operator.and_,
    'or': operator.or_
}

def get_place_details(place_id):
    response = requests.get(f'https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={GMAPS_API_KEY}')
    try:
        return json.loads(response.text)['result']
    except KeyError:
        raise KeyError('Key \'result\' not found in the response')

# Add parameters for the search query.
parser = argparse.ArgumentParser()
parser.add_argument('--query', type=str, help='Search query for Google Maps API')
parser.add_argument('--output_dir', type=str, help='Directory to save the output CSV file')
parser.add_argument('--min_rating', type=float, help='Minimum rating of the place(s)')
parser.add_argument('--min_reviews', type=int, help='Minimum number of reviews for the place(s)')
parser.add_argument('--operator', default='and', choices=LOGICAL_OPERATORS.keys(), type=str,
                    help='Logical operator to apply between rating and reviews count')
parser.add_argument('--exclude', '-e', choices=PLACE_CATEGORIES, nargs='+', type=str,
                    help='Exclude specific types of places from the query results')
parser.add_argument('--lang', default='en', choices=['en', 'fr', 'de'], type=str,
                    help='Language for the Wikipedia link')
parser.add_argument('--summary_len', type=int,
                    help='Limit the number of sentences in the Wikipedia summary')

args = parser.parse_args()
# Fetch the data.
response = requests.get(f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={args.query}&language=en&key={GMAPS_API_KEY}')
# Convert the response to a JSON object.
places_data = json.loads(response.text)['results']
if not places_data:
    raise Exception(f'No results found for query: {args.query}')

# Create the directory if it doesn't exist.
pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)
# Make the filename more readable.
query_terms = args.query.split(' ')
output_filename = ' '.join([term.capitalize() for term in query_terms])
# Set Wikipedia language.
wikipedia.set_lang(args.lang)

header = ['name', 'coordinates', 'types', 'rating', 'formatted_address', 'summary', 'url', 'reviews']
with open(args.output_dir + f'/{output_filename}.csv', 'w', encoding='utf-8') as file:
    csv_writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_ALL)
    csv_writer.writerow(header)
    for place in places_data:
        place_name = place['name']
        address = place['formatted_address']
        place_types = place['types']
        reviews_count = place.get('user_ratings_total', -1)
        place_rating = place.get('rating', -1)

        try:
            if args.summary_len:
                wiki_page = wikipedia.page(place_name, sentences=args.summary_len)
            else:
                wiki_page = wikipedia.page(place_name)
            wiki_url = wiki_page.url
            wiki_summary = wiki_page.summary.replace('\n', '')
        except KeyboardInterrupt:
            exit(-1)
        except:
            wiki_url, wiki_summary = '', ''

        # Exclude places based on the provided list.
        if args.exclude and set(args.exclude).intersection(set(place_types)):
            continue

        # Apply rating and review filters.
        if args.min_rating and args.min_reviews:
            if not LOGICAL_OPERATORS[args.operator](place_rating >= args.min_rating, reviews_count >= args.min_reviews):
                continue
        elif args.min_rating and place_rating < args.min_rating:
            continue
        elif args.min_reviews and reviews_count < args.min_reviews:
            continue

        lat, lng = place['geometry']['location']['lat'], place['geometry']['location']['lng']
        row_data = [place_name, (lat, lng), ', '.join(place_types), place_rating, address, wiki_summary, wiki_url, reviews_count]
        print(f'Processing {output_filename}: {row_data}')
        csv_writer.writerow(row_data)
