from datetime import date, timedelta
import pandas as pd
import argparse
import datetime

url = "https://raw.githubusercontent.com/thepanacealab/covid19_twitter/master/dailies/"
attrs = [
         {'type': '_top1000terms',
          'name': 'all_terms.csv'},
         {'type': '_top1000bigrams',
          'name': 'all_bigrams.csv'},
         {'type': '_top1000trigrams',
          'name': 'all_trigrams.csv'}
         ]


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--from', dest='from_date', type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'),
        default=datetime.date.today() - datetime.timedelta(days=1))
    parser.add_argument(
        '--to', dest='to_date', type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'),
        default=datetime.date.today())
    parser.add_argument(
        '--mode', dest='mode', type=str, default='update')

    args = parser.parse_args()
    from_date = args.from_date
    to_date = args.to_date

    delta = to_date - from_date       # as timedelta

    for item in attrs:

        if args.mode == 'update':
            df = pd.read_csv('../' + item['name'], index_col=[0])
            result = pd.concat([df, collect_data(item['type'], delta, from_date)])
            result.to_csv('../' + item['name'])
        elif args.mode == 'new':
            df = collect_data(item['type'], delta, from_date)
            df.to_csv('../' + item['name'])




def collect_data(name, delta, from_date):

    tmp = []

    for i in range(delta.days + 1):
        day = from_date + timedelta(days=i)
        path = url + str(day).split(' ')[0] + '/' + str(day).split(' ')[0] + name + '.csv'
        tmp_df = pd.read_csv(path, error_bad_lines=False, index_col=None, header=0, names=['term','counts'])
        tmp_df['date'] = str(day).split(' ')[0]
        tmp.append(tmp_df)

    df = pd.concat(tmp, axis=0, ignore_index=True)
    df['counts'] = pd.to_numeric(df['counts'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.reset_index(inplace=True, drop=True)

    return df



if __name__ == "__main__":
    main()