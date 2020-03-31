#!/usr/bin/env python3
#
# Sample row from parsed CSV file:
# ['YYYY/MM/DD', 'new_cases', 'curr_cases', 'new_cases_pct', 'new_deaths', 'cur_deaths', 'fetch_url']

import csv
import datetime
import pandas
import re
import urllib.request

CSV_FILE = 'covid-19-daily.csv'

FETCH_URL = 'https://www.sfdph.org/dph/alerts/coronavirus.asp'
FETCH_RE_CASES = re.compile(r'.*<p>Total Positive Cases: (\d+)\s*</p>.*')
FETCH_RE_DEATHS = re.compile(r'.*<p>Deaths: (\d+)\s*</p>.*')


def main():
    prev_cases, prev_deaths = read_previous()

    curr_cases, curr_deaths = fetch_curr()

    write_new(prev_cases, prev_deaths, curr_cases, curr_deaths)

    write_image()


def write_image():
    df = pandas.read_csv(CSV_FILE)
    fig = df.plot(secondary_y=('New cases', 'New deaths')).get_figure()
    fig.savefig('covid-19-fig.png')


def write_new(prev_cases, prev_deaths, curr_cases, curr_deaths):
    new_cases = curr_cases - prev_cases
    new_cases_pct = new_cases / prev_cases * 100
    new_deaths = curr_deaths - prev_deaths
    date = datetime.datetime.now().strftime('%Y/%m/%d')

    csv_line = ('%s,%d,%d,%i%%,%d,%d,%s\n' % (
        date, new_cases, curr_cases, new_cases_pct,
        new_deaths, curr_deaths,
        FETCH_URL))

    with open(CSV_FILE, 'a') as f:
        f.write(csv_line)

    return


def read_previous():
    with open(CSV_FILE, 'r') as f:
        cr = csv.reader(f.readlines())
        prev = list(cr)[-1]
        return int(prev[2]), int(prev[5])


def fetch_curr():
    curr_cases = 0
    curr_deaths = 0

    with urllib.request.urlopen(FETCH_URL) as response:
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