"""Fetch complete UTC weeks and calculate auditable forecast errors (stdlib only)."""
import argparse
import csv
import datetime as dt
import json
from pathlib import Path
import statistics
import urllib.request

BASE = 'https://api.carbonintensity.org.uk'
ROOT = Path(__file__).resolve().parents[1]


def fetch(endpoint, start, end):
    url = f'{BASE}/{endpoint}/{start}/{end}'
    with urllib.request.urlopen(url, timeout=60) as response:
        payload = json.load(response)
    # API also returns the period ending at start; filter by interval START.
    rows = [r for r in payload['data'] if f'{start}T00:00Z' <= r['from'] < f'{end}T00:00Z']
    expected = [(dt.datetime.combine(start, dt.time(), dt.timezone.utc) + dt.timedelta(minutes=30*i)).strftime('%Y-%m-%dT%H:%MZ') for i in range(336)]
    if sorted(r['from'] for r in rows) != expected:
        raise ValueError(f'{url}: incomplete or duplicate half-hourly observations')
    return url, payload, sorted(rows, key=lambda r:r['from'])


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', type=dt.date.fromisoformat, default=dt.date(2026,9,27))
    parser.add_argument('--weeks', type=int, default=4)
    parser.add_argument('--first-week', type=int, default=14)
    args = parser.parse_args()
    if args.weeks < 1:
        parser.error('--weeks must be positive')
    summaries = []
    for offset in range(args.weeks):
        start = args.start + dt.timedelta(days=7*offset)
        end = start + dt.timedelta(days=7)
        if dt.datetime.combine(end, dt.time(), dt.timezone.utc) > dt.datetime.now(dt.timezone.utc):
            raise ValueError('Only completed UTC weeks can be analysed')
        week = args.first_week + offset
        folder = ROOT / 'data' / f'week{week}'
        folder.mkdir(parents=True, exist_ok=True)
        provenance = {'retrieved_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'start_inclusive_utc': str(start), 'end_exclusive_utc': str(end), 'sources': {}}
        tables = {}
        for endpoint in ('intensity', 'generation'):
            url, payload, rows = fetch(endpoint, start, end)
            (folder / f'{endpoint}_raw.json').write_text(json.dumps(payload, indent=2)+'\n')
            provenance['sources'][endpoint] = url
            tables[endpoint] = rows
        observations = []
        for row in tables['intensity']:
            forecast, actual = row['intensity']['forecast'], row['intensity']['actual']
            if forecast is None or actual is None:
                raise ValueError(f'Missing forecast/actual: {row["from"]}')
            error = actual - forecast
            observations.append({'from_utc':row['from'], 'to_utc':row['to'], 'forecast_gco2_kwh':forecast, 'actual_gco2_kwh':actual, 'error_actual_minus_forecast':error, 'absolute_error':abs(error)})
        write_csv(folder/'intensity.csv', observations)
        mix = [{'from_utc':r['from'], 'to_utc':r['to'], **{x['fuel']:x['perc'] for x in r['generationmix']}} for r in tables['generation']]
        write_csv(folder/'generation.csv', mix)
        errors = [r['error_actual_minus_forecast'] for r in observations]
        band = lambda hours: statistics.mean(r['error_actual_minus_forecast'] for r in observations if int(r['from_utc'][11:13]) in hours)
        summary = {'week':week, 'start_utc':str(start), 'end_exclusive_utc':str(end), 'observations':len(observations), 'mae':statistics.mean(abs(e) for e in errors), 'mean_signed_error':statistics.mean(errors), 'overnight_bias':band({23,0,1,2,3,4,5,6,7}), 'afternoon_bias':band({15,16,17}), 'max_absolute_error':max(abs(e) for e in errors), 'errors_over_50':sum(abs(e)>50 for e in errors)}
        summaries.append(summary)
        (folder/'provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
        print(json.dumps(summary), flush=True)
    write_csv(ROOT/'data'/'weekly_summary.csv', summaries)


if __name__ == '__main__':
    main()
