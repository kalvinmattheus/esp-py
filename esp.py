import json
import os
from datetime import datetime

import requests

script_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.join(script_dir, 'conf.txt')
try:
    conf = open(conf_dir, 'r')
except FileNotFoundError:
    conf = open('conf.txt', 'w')
    conf.writelines(['token:XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX\n',
                     'municipal:eskom\n',
                     'area:eskde-10-fourwaysext10cityofjohannesburggauteng\n'])
    conf.close()
    print('Please complete fill in the conf.txt file before running esp-py.')
    print('First get a token from https://eskomsepush.gumroad.com/l/api')
    print('Second find your area id with curl --location --request GET '
          '"https://developer.sepush.co.za/business/2.0/areas_search?text=fourways" '
          '--header "token: LICENSE_KEY"')
    exit(1)

token = conf.readline().split(':')[1][:-1]
municipal = conf.readline().split(':')[1][:-1]
area = conf.readline().split(':')[1][:-1]


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
    delta = int(end_time[:2]) - int(start_time[:2])
    delta = delta + 24 if delta < 0 else delta
    if delta < 4:
        print(f'> {day} from {start_time} until {end_time} on {stage}')
    else:
        print(f'> {day} from {start_time} until \033[91m{end_time}\033[0m on {stage}')


def print_allowance(a):
    count = a['count']
    limit = a['limit']
    remaining = int((limit - count) / 2)
    print(f'You have {remaining} requests remaining for today.')


def get_stage(t, m):
    url = 'https://developer.sepush.co.za/business/2.0/status'
    headers = {'token': t}
    response = requests.get(url, headers=headers)
    return json.loads(response.text)['status'][m]['stage']


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
        stage = get_stage(token, municipal)
        if int(stage) <= 0:
            print(f'There is currently no load shedding!')
        else:
            print(f'The current load shedding stage is: \033[1mStage {stage}\033[0m')
            schedule = get_schedule(area, token)
            print(f'\033[1mThe next load shedding events are scheduled for:\033[0m')
            for event in schedule:
                print_event(event)
        allowance = get_allowance(token)
        print_allowance(allowance)
