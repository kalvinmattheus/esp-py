import json
from datetime import datetime

import requests

# First get a token from https://eskomsepush.gumroad.com/l/api
token = 'XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX'
# Second find your area id with curl --location --request GET \
# 'https://developer.sepush.co.za/business/2.0/areas_search?text=fourways' \
# --header 'token: LICENSE_KEY'
area = 'eskde-10-fourwaysext10cityofjohannesburggauteng'


def get_date_description(date_string):
    input_date = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z').date()
    today = datetime.now().date()
    delta = (input_date - today).days
    if delta == 0:
        return 'Today'
    elif delta == 1:
        return 'Tomorrow'
    else:
        return f'In {delta} days'


def get_time_from_date_string(date_string):
    date_time = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z')
    time_string = date_time.strftime('%H:%M')
    return time_string


def print_event(e):
    day = get_date_description(e['start'])
    start_time = get_time_from_date_string(e['start'])
    end_time = get_time_from_date_string(e['end'])
    stage = e['note']
    print(f'> {day} from {start_time} until {end_time} on {stage}')


def print_allowance(a):
    count = a['count'] + 2  # add two requests made in current run
    limit = a['limit']
    remaining = int((limit - count) / 2)
    print(f'You have {remaining} requests remaining for today.')


def get_stage(t):
    url = 'https://developer.sepush.co.za/business/2.0/status'
    headers = {'token': t}
    response = requests.get(url, headers=headers)
    return json.loads(response.text)['status']['eskom'][
        'stage']  # replace eskom with capetown if relevant


def get_schedule(a, t):
    url = 'https://developer.sepush.co.za/business/2.0/area?id=' + a
    headers = {'token': t}
    response = requests.get(url, headers=headers)
    return json.loads(response.text)['events']


def get_allowance(t):
    url = 'https://developer.sepush.co.za/business/2.0/api_allowance'
    headers = {'token': t}
    response = requests.get(url, headers=headers)
    return json.loads(response.text)['allowance']


if __name__ == '__main__':
    allowance = get_allowance(token)
    if allowance['count'] == allowance['limit']:
        print('You cannot make any more requests, try again tomorrow...')
    else:
        stage = get_stage(token)
        schedule = get_schedule(area, token)
        print(f'The next loadsheading events are scheduled for (stage {stage}):')
        for event in schedule:
            print_event(event)
        print_allowance(allowance)
