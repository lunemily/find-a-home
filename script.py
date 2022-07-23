import csv
import logging
import os
import sys
from time import sleep

from lxml import etree, html
from lxml.etree import Element
import requests

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome import options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.remote.webelement import WebElement
# from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# driver = webdriver.Chrome

metros = [
    {
        'state': 'ct',
        'metro': 'Bridgeport-Stamford-Norwalk',
        'msa_id': '14860',
    },
    {
        'state': 'ct',
        'metro': 'New Haven-Milford',
        'msa_id': '35300',
    },
    {
        'state': 'me',
        'metro': 'Portland-South Portland',
        'msa_id': '38860',
    },
    {
        'state': 'md',
        'metro': 'Baltimore-Columbia-Towson',
        'msa_id': '12580',
    },
    {
        'state': 'ma',
        'metro': 'Boston-Cambridge-Newton',
        'msa_id': '14460',
    },
    {
        'state': 'ma',
        'metro': 'Worcester',
        'msa_id': '49340',
    },
    {
        'state': 'nj',
        'metro': 'New York-Newark-Jersey City',
        'msa_id': '35620',
    },
    {
        'state': 'nj',
        'metro': 'Philadelphia-Camden-Wilmington',
        'msa_id': '37980',
    },
    {
        'state': 'ny',
        'metro': 'New York-Newark-Jersey City',
        'msa_id': '35620',
    },
    {
        'state': 'Providence-Warwick',
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

best_places_city_base_url = 'https://www.bestplaces.net/'

best_places_city_url =                      '//div[@class="col-md-4"]/ul/li/a'
best_places_city_population =               '//u[contains(text(),"Population")]/../../following-sibling::p[1]'
best_places_city_med_income =               '//u[contains(text(),"Median Income")]/../../following-sibling::p[1]'
best_places_city_med_age =                  '//u[contains(text(),"Median Age")]/../../following-sibling::p[1]'
best_places_city_unempl_rate =              '//u[contains(text(),"Unemployment Rate")]/../../following-sibling::p[1]'
best_places_city_med_home =                 '//u[contains(text(),"Median Home Price")]/../../following-sibling::p[1]'
best_places_city_comfort =                  '//u[contains(text(),"Comfort Index (Climate)")]/../../following-sibling::p[1]'
best_places_city_county =                   '//b[text()="County:"]/following-sibling::u[1]/a'
best_places_city_primary_zip_code =         '//b[text()="Zip Codes:"]/../a[1]/u'
best_places_city_cost_of_living =           '//b[text()="Cost of Living:"]/following-sibling::text()[1]'
best_places_jobs_future_jobs =              ''
best_places_health_cost_index =             ''
best_places_health_water_quality_index =    ''
best_places_health_superfund_index =        ''
best_places_health_air_quality_index =      ''
best_places_voting_vote_word =              ''



niche_summary_grade_overall =               '//div[@class="overall-grade"]'  # /div/div/span/following-sibling::text()
# and all niche grades
niche_residents_poverty =                   ''
niche_residents_community_percent =         ''
niche_residents_lgbtq_percent =             ''
niche_residents_lgbtq_acceptance_level =    ''

area_vibes_livibility_total =               ''
# and other scores on livibility
area_vibes_livibility_usa_rank =            ''
# all crime from table



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
    logging.info(f'City URL: {city_link}')
    city = {
        'state': metro.get('state'),
        'metro': metro.get('metro'),
        'metro_id': metro.get('msa_id'),
        'city': city_element[0].text,
    }

    # Get city information
    # Best Places

    city_page: etree = get_page(city_link.replace('..', best_places_city_base_url))

    city['county']              = str(city_page.xpath(best_places_city_county)[0].text).replace('County','').strip()
    city['zip_code']            = str(city_page.xpath(best_places_city_primary_zip_code)[0].text)
    city['population']          = str(city_page.xpath(best_places_city_population)[0].text)
    city['unemployment']        = str(city_page.xpath(best_places_city_unempl_rate)[0].text)
    city['median_income']       = str(city_page.xpath(best_places_city_med_income)[0].text)
    city['median_home_price']   = str(city_page.xpath(best_places_city_med_home)[0].text)
    city['median_age']          = str(city_page.xpath(best_places_city_med_age)[0].text)
    city['comfort_index']       = str(city_page.xpath(best_places_city_comfort)[0].text)
    city['cost_of_living']      = str(city_page.xpath(best_places_city_cost_of_living)[0]).strip()

    niche_page: etree = get_page(f'https://www.niche.com/places-to-live/{city["city"]}-{city["county"]}-{city["state"]}/')
    print(etree.tostring(niche_page))

    city_attribute = niche_page.xpath(niche_summary_grade_overall)
    logging.info(city_attribute)

    city['niche_grade']         = str('')

    return city


def save_city(city: dict):
    filename = f'output/{city.get("metro")}.csv'
    with open(file=filename, mode='w+') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[key for key in city], delimiter=',', quotechar='\"', quoting=csv.QUOTE_NONNUMERIC)

        writer.writeheader()
        writer.writerow(city)


def parse_and_save_city(metro: dict, city_element: etree.Element):
    city = parse_city(metro=metro, city_element=city_element)

    # If city already in file, move on to next one
    filename = f'output/{metro.get("metro")}.csv'
    with open(file=filename, mode='w+') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        logging.info(f'Searching for {city["city"]} in {filename}')
        for row in reader:
            logging.info(row)
            if city['city'] == row['city']:
                logging.INFO(f'{city["city"]} found in {filename}. Skipping.')
                return None
    logging.info(f'{city["city"]} not found in {filename}. Saving.')
    save_city(city=city)


def main():
    for metro in metros:
        best_places_url = f'https://www.bestplaces.net/find/state.aspx?state={metro.get("state")}&msa={metro.get("msa_id")}'
        logging.info(f'Gathering information for {metro.get("metro")}')
        logging.info(f'Best places URL: {best_places_url}')

        metro_page = get_page(best_places_url)
        metro_cities = metro_page.xpath(best_places_city_url)

        for city in metro_cities:
            parse_and_save_city(metro=metro, city_element=city)
            sleep(60)

        sleep(5)


setup()

main()

tear_down()
