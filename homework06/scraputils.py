import re
from time import sleep

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


def extract_news(parser):
    """ Extract news from a given web page """
    news_list = []
    now_parsing = {}
    try:
        not_parsed = parser.find_all('table')[2]
    except IndexError:
        return ''
    for elem in not_parsed:
        if isinstance(elem, NavigableString):
            continue
        if isinstance(elem, Tag):
            if elem.get('class'):
                if elem.get('class')[0] == 'athing':
                    elemtitle = elem.find_all('td')[2].find_all('a')
                    now_parsing['title'] = elemtitle[0].text
                    now_parsing['url'] = elemtitle[0].get('href')
                if elem.get('class')[0] == 'spacer':
                    news_list.append(now_parsing)
                    now_parsing = {}
            else:
                if elem.find('td', {'class': 'subtext'}):
                    elemspan = elem.find_all('td')[1]
                    now_parsing['author'] = elemspan.find_all("a", {"class": "hnuser"})[0].text
                    points = elemspan.find_all("span", {"class": "score"})[0].text
                    comments = elemspan.find_all('a')[-1].text
                    if comments == 'discuss':
                        now_parsing['comments'] = 0
                    else:
                        now_parsing['comments'] = int(''.join(re.findall(r'\d', comments)))
                    now_parsing['points'] = int(''.join(re.findall(r'\d', points)))
    return news_list


def extract_next_page(parser):
    """ Extract next page URL """
    try:
        return parser.find_all('a', {'class': 'morelink'})[0].get('href')
    except IndexError:
        return 'newest'


def get_news(url, n_pages=1):
    """ Collect news from a given web page """
    news = []
    while n_pages:
        sleep(10)
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)
        n_pages -= 1
    return news
