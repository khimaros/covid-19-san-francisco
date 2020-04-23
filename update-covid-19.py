#!/usr/bin/env python3
#
# Sample row from parsed CSV file:
# ['YYYY/MM/DD', 'new_cases', 'curr_cases', 'new_cases_pct', 'new_deaths', 'cur_deaths', 'fetch_url']

import csv
import datetime
import os
import pandas
import pytz
import re
import sys
import urllib.request
import matplotlib 

CSV_FILE = 'covid-19-daily.csv'

FETCH_URL = 'https://www.sfdph.org/dph/alerts/coronavirus.asp'
FETCH_RE_CASES = re.compile(r'.*<p>Total Positive Cases: (\d+)\s*</p>.*')
FETCH_RE_DEATHS = re.compile(r'.*<p>Deaths: (\d+)\s*')


def main():
    response_file = ''
    if len(sys.argv) == 2:
         response_file = sys.argv[1]

    prev_date, prev_cases, prev_deaths = read_previous()


    curr_cases = curr_deaths = 0
    if response_file:
        curr_cases, curr_deaths = load_curr(response_file)
    else:
        curr_cases, curr_deaths = fetch_curr()

    curr_date = datetime.datetime.now(tz=pytz.timezone('US/Pacific')).strftime('%Y/%m/%d')
    if curr_date != prev_date:
        write_new(prev_cases, prev_deaths, curr_cases, curr_deaths, curr_date)

    write_image()


def write_image():
    df = pandas.read_csv(CSV_FILE)
    matplotlib.rcParams.update({'figure.autolayout': True})
    fig1 = df.plot('Date', secondary_y=('New cases', 'New deaths', 'Cumulative deaths'), rot=30, title='Linear Scale').get_figure()
    fig1.savefig('covid-19-fig.png')
    fig2 = df.plot('Date', rot=30, title='Log Scale', logy=True)
    fig2.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    fig2.figure.savefig('covid-19-log-fig.png')


def write_new(prev_cases, prev_deaths, curr_cases, curr_deaths, curr_date):
    new_cases = curr_cases - prev_cases
    new_cases_pct = new_cases / prev_cases * 100
    new_deaths = curr_deaths - prev_deaths

    csv_line = ('%s,%d,%d,%i%%,%d,%d,%s\n' % (
        curr_date, new_cases, curr_cases, new_cases_pct,
        new_deaths, curr_deaths,
        FETCH_URL))

    with open(CSV_FILE, 'a') as f:
        f.write(csv_line)

    return


def read_previous():
    with open(CSV_FILE, 'r') as f:
        cr = csv.reader(f.readlines())
        prev = list(cr)[-1]
        return prev[0], int(prev[2]), int(prev[5])


def fetch_curr():
    curr_cases = 0
    curr_deaths = 0

    with urllib.request.urlopen(FETCH_URL) as response:
        return read_curr(response)


def load_curr(path):
    with open(path, 'r') as f:
        return read_curr(f)


def read_curr(response):
    for line in response.readlines():
        m = FETCH_RE_CASES.match(str(line))
        if m:
            curr_cases = m.groups()[0]

        m = FETCH_RE_DEATHS.match(str(line))
        if m:
            curr_deaths = m.groups()[0]

    return int(curr_cases), int(curr_deaths)


if __name__ == '__main__':
    main()
