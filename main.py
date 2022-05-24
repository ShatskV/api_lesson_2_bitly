import argparse
import os

import requests
from dotenv import load_dotenv


URL_API_BITLY = 'https://api-ssl.bitly.com/v4/{route}'
ROUTE_USER = '/user'
ROUTE_SHORTEN = '/shorten'
ROUTE_ALL_CLICKS = '/bitlinks/{link}/clicks/summary'
ROUTE_BITLINK_INFO = '/bitlinks/{link}'


def parse_url_from_terminal():
    parser = argparse.ArgumentParser(
    description='Описание что делает программа:'
                )
    parser.add_argument('url', help="ссылка для сокращения или "
                        "ссылка bit.ly для получения количества переходов по ней"
                        )
    args = parser.parse_args()
    url = args.url
    return url


def shorten_link(headers, link, url):
    payload = {"long_url": link}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    api_answer = response.json()
    return api_answer.get('link')


def is_bitlink(headers, link, url_for_api_request):
    url = url_for_api_request.format(link=link)
    response = requests.get(url, headers=headers)
    return response.ok


def count_clicks(headers, link, url_api_for_request):
    url = url_api_for_request.format(link=link)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    api_answer = response.json()
    return f"Количество переходов по ссылке битли: {api_answer.get('total_clicks')}"


def drop_url_scheme(link):
    link = link.strip()
    args = link.split('://')
    return args[1] if len(args) > 1 else link
    

def main():
    load_dotenv()
    bitly_token = os.getenv('BITLY_TOKEN')
    headers = {'Authorization': f'Bearer {bitly_token}'}
    link = parse_url_from_terminal()
    url_api = URL_API_BITLY.format(route=ROUTE_BITLINK_INFO)
    host_url = drop_url_scheme(link)
    is_short_url = is_bitlink(headers, host_url, url_api)
    if is_short_url:
        url_api_for_request = URL_API_BITLY.format(route=ROUTE_ALL_CLICKS)
        action_func = count_clicks
        link = host_url
    else:
        url_api_for_request = URL_API_BITLY.format(route=ROUTE_SHORTEN)
        action_func = shorten_link
    try:
        api_answer = action_func(headers, link, url_api_for_request)
    except requests.exceptions.HTTPError as e:
        api_answer = f"Error: {e}"
    print(api_answer)


if __name__ == '__main__':
    main()
