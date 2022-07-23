import csv
import logging
import os
import sys
from time import sleep

from lxml import etree, html
from lxml.etree import Element
import requests

requests.packages.urllib3.disable_warnings()

log_file = 'cities.log'
logging.basicConfig(filename=log_file, level=logging.INFO)

metros = [
    {
        'state_code': 'ct',
        'metro': 'Bridgeport-Stamford-Norwalk',
        'msa_id': '14860',
    },
    {
        'state_code': 'ct',
        'metro': 'New Haven-Milford',
        'msa_id': '35300',
    },
    {
        'state_code': 'me',
        'metro': 'Portland-South Portland',
        'msa_id': '38860',
    },
    {
        'state_code': 'md',
        'metro': 'Baltimore-Columbia-Towson',
        'msa_id': '12580',
    },
    {
        'state_code': 'ma',
        'metro': 'Boston-Cambridge-Newton',
        'msa_id': '14460',
    },
    {
        'state_code': 'ma',
        'metro': 'Worcester',
        'msa_id': '49340',
    },
    {
        'state_code': 'nj',
        'metro': 'New York-Newark-Jersey City',
        'msa_id': '35620',
    },
    {
        'state_code': 'nj',
        'metro': 'Philadelphia-Camden-Wilmington',
        'msa_id': '37980',
    },
    {
        'state_code': 'ny',
        'metro': 'New York-Newark-Jersey City',
        'msa_id': '35620',
    },
    {
        'state_code': 'Providence-Warwick',
        'metro': 'Bridgeport',
        'msa_id': '39300',
    },
]

csv_columns = [
    'State',
    'City',
    # Best Places
    # Summary
    'Population',
    'Median Income',
    'Median Home Price',
    'Comfort Index (Climate)',
    'County',
    'Metro Area',
    'Zip Codes',
    'Primary Zip Code',
    'Pros',
    'Cons',
    # Jobs
    'Income per Capita',
    'Unemployment Rate',
    'Recent Job Growth',
    'Future Job Growth',
    'You Should Know',
    # Crime
    'Violent Crime',
    'Property Crime',
    # Climate
    'Rain',
    'Snow',
    'Sunny Days',
    'Precipitation Days',
    'Summer High',
    'Winter Low',
    # Economy
    'Sales Tax Rate',
    'Income Tax Rate',
    # Health
    'Health Cost Index',
    'Water Quality Index',
    'Superfund Index',
    'Air Quality Index',
    # People
    'Population Density',
    'White Percent',
    'Black Percent',
    'Asian Percent',
    'Hispanic Percent',
    'DINK Percent',
    # Politics
    'Political Climate',
    'VoteWord'
    # Housing
    'Home Appreciation 10y',  # ???
    'Home Appreciation',
    'Average Home Age',
    'Renting Rate',
    'Property Tax Rate',
    # Transportation
    'One-Way Commute',
    'Mass Transit Rate',

    # Niche
    # Summary
    'Overall Niche Grade',
    'Public Schools Grade',
    'Housing Grade',
    'Families Grade',
    'Jobs Grade',
    'Cost of Living Grade',
    'Outdoor Activities Grade',
    'Crime Grade',
    'Nightlife Grade',
    'Diversity Grade',
    'Weather Grade',
    'Health Grade',
    'Commute Grade',
    # Real Estate
    'Area Feel',
    'Own Percent',
    # Crime
    #
    # I'm ignoring this section
    #
    # Residents
    'Higher Degree Percent',
    # Working
    'Median Household Income',
    'Best Places Rank',

    # Area Vibes
    # Summary
    'Livability',
    # Locals' Thoughts
    'Family Friendly',
    'Public Transit Accessible',
    'Walkable Groceries',
    
]

best_places_city_base_url = 'https://www.bestplaces.net'

best_places_city_url =                      '//div[@class="col-md-4"]/ul/li/a'
best_places_city_state =                    '//b[text()="State:"]/following-sibling::u[1]/a'
best_places_city_population =               '//u[contains(text(),"Population")]/../../following-sibling::p[1]'
best_places_city_med_income =               '//u[contains(text(),"Median Income")]/../../following-sibling::p[1]'
best_places_city_med_age =                  '//u[contains(text(),"Median Age")]/../../following-sibling::p[1]'
best_places_city_unempl_rate =              '//u[contains(text(),"Unemployment Rate")]/../../following-sibling::p[1]'
best_places_city_med_home =                 '//u[contains(text(),"Median Home Price")]/../../following-sibling::p[1]'
best_places_city_comfort =                  '//u[contains(text(),"Comfort Index (Climate)")]/../../following-sibling::p[1]'
best_places_city_county =                   '//b[text()="County:"]/following-sibling::u[1]/a'
best_places_city_primary_zip_code =         '//b[text()="Zip Codes:"]/../a[1]/u'
best_places_city_cost_of_living =           '//b[text()="Cost of Living:"]/following-sibling::text()[1]'
best_places_jobs_future_jobs =              '//u[text()="Future Job Growth"]/../../following-sibling::td[1]'
best_places_health_cost_index =             '//h6[text()="HEALTH COST INDEX"]/following-sibling::div[1]'
best_places_health_water_quality_index =    '//h6[text()="WATER QUALITY INDEX"]/following-sibling::div[1]'
best_places_health_superfund_index =        '//h6[text()="SUPERFUND INDEX"]/following-sibling::div[1]'
best_places_health_air_quality_index =      '//h6[text()="AIR QUALITY INDEX"]/following-sibling::div[1]'
best_places_voting_vote_word =              '//h5[text()="VoteWord™"]/following-sibling::h5[1]'

area_vibes_livibility_total =               '//img[contains(@alt, "livability")]/following-sibling::em[1]'



def setup():
    for metro_area in metros:
        filename = f'output/{metro_area.get("metro")}.csv'
        if not os.path.isfile(filename):
            with open(file=filename,mode='w+') as state_csv:
                state_csv.write('')


def tear_down():
    logging.info('Exiting')


def get_page(url: str) -> etree:
    logging.info(f'Requesting page at {url}')
    response = requests.get(url=url, verify=False, allow_redirects=True)
    return html.fromstring(response.content)


def parse_city(metro: dict, city_element: etree.Element):
    city_link: str = city_element.attrib['href'].replace('..', best_places_city_base_url)
    city_name: str = city_element[0].text
    logging.info(f'Getting information about {city_name}')
    city = {}

    # Get city information
    # Best Places
    # Summary Page + inputs
    city_page: etree = get_page(city_link.replace('..', best_places_city_base_url))

    city['state']                   = str(city_page.xpath(best_places_city_state)[0].text).strip()
    city['state_code']              = str.upper(metro.get('state_code'))
    city['metro']                   = metro.get('metro')
    city['metro_id']                = metro.get('msa_id')
    city['city']                    = city_name
    city['county']                  = str(city_page.xpath(best_places_city_county)[0].text).replace('County','').strip()
    try:
        city['zip_code']            = str(city_page.xpath(best_places_city_primary_zip_code)[0].text)
    except IndexError as e:
        logging.error('Zip Code not available')
        city['zip_code']            = 'None'
    city['population']              = str(city_page.xpath(best_places_city_population)[0].text)
    city['unemployment']            = str(city_page.xpath(best_places_city_unempl_rate)[0].text)
    city['median_income']           = str(city_page.xpath(best_places_city_med_income)[0].text)
    city['median_home_price']       = str(city_page.xpath(best_places_city_med_home)[0].text)
    city['median_age']              = str(city_page.xpath(best_places_city_med_age)[0].text)
    city['summer_comfort_index']    = str.split(city_page.xpath(best_places_city_comfort)[0].text, ' / ')[0]
    city['winter_comfort_index']    = str.split(city_page.xpath(best_places_city_comfort)[0].text, ' / ')[1]
    city['cost_of_living']          = str(city_page.xpath(best_places_city_cost_of_living)[0]).strip()

    sleep(1)

    # Jobs Page
    city_jobs_page: etree = get_page(url=f'https://www.bestplaces.net/jobs/city/{city["state"]}/{city["city"]}')

    city['future_job_growth']   = str(city_jobs_page.xpath(best_places_jobs_future_jobs)[0].text)

    sleep(1)

    # Health Page
    city_health_page: etree = get_page(url=f'https://www.bestplaces.net/health/city/{city["state"]}/{city["city"]}')

    city['health_cost_index']   = str(city_health_page.xpath(best_places_health_cost_index)[0].text).strip()
    city['water_quality_index'] = str(city_health_page.xpath(best_places_health_water_quality_index)[0].text).strip()
    city['superfund_index']     = str(city_health_page.xpath(best_places_health_superfund_index)[0].text).strip()
    city['air_quality_index']   = str(city_health_page.xpath(best_places_health_air_quality_index)[0].text).strip()

    sleep(1)

    # Voting Page
    city_voting_page: etree = get_page(url=f'https://www.bestplaces.net/voting/city/{city["state"]}/{city["city"]}')

    city['voteword']    = str.split(city_voting_page.xpath(best_places_voting_vote_word)[0].text, ':')[1].strip()

    # Area Vibes
    area_vibes_page: etree = get_page(url=f'https://www.areavibes.com/{city["city"]}-{city["state_code"]}')

    try:
        city['livability_score']    = str(area_vibes_page.xpath(area_vibes_livibility_total)[0].text)
    except IndexError as e:
        logging.error('City not found on Area Vibes')
        city['livability_score']    = 'None'

    return city


def save_city(city: dict):
    filename = f'output/{city.get("metro")}.csv'
    with open(file=filename, mode='a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[key for key in city], delimiter=',', quotechar='\"', quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')
        if os.stat(filename).st_size == 0:
            writer.writeheader()
        writer.writerow(city)


def parse_and_save_city(metro: dict, city_element: etree.Element):
    # If city already in file, move on to next one
    filename = f'output/{metro.get("metro")}.csv'
    city_name: str = city_element[0].text

    with open(file=filename, mode='r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        logging.info(f'Searching for {city_name} in {filename}')
        for row in reader:
            if city_name == row['city']:
                logging.warning(f'{city_name} found in {filename}. Skipping.')
                return None
    logging.info(f'{city_name} not found in {filename}. Saving.')
    city = parse_city(metro=metro, city_element=city_element)
    save_city(city=city)


def main():
    for metro in metros:
        best_places_url = f'https://www.bestplaces.net/find/state.aspx?state={metro.get("state_code")}&msa={metro.get("msa_id")}'
        logging.info(f'Gathering information for {metro.get("metro")}')
        logging.info(f'Best places URL: {best_places_url}')

        metro_page = get_page(best_places_url)
        metro_cities = metro_page.xpath(best_places_city_url)

        for city in metro_cities:
            parse_and_save_city(metro=metro, city_element=city)
            sleep(5)

        sleep(5)


setup()

main()

tear_down()
