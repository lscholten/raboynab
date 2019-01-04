from os.path import basename, splitext
import pandas as pd
import click

@click.command()
@click.argument('input_path', type=click.Path(exists=True))
def convert(input_path):
    transactions_path = click.format_filename(input_path)
    rabo = pd.read_csv(transactions_path, encoding = 'latin1')

    df_ynab = pd.DataFrame({
        'Account': rabo['IBAN/BBAN'],
        'Date': [x.strftime('%Y-%m-%d') for x in pd.to_datetime(rabo['Datum'])],
        'Payee': [x if not pd.isnull(x) else '' for x in rabo['Naam tegenpartij']],
        'Category': ['' for x in rabo['IBAN/BBAN']],
        'Memo': rabo['Omschrijving-1'],
        'Outflow': [x.replace('-', '').replace(',', '.') if '-' in x else '' for x in rabo['Bedrag']],
        'Inflow': [x.replace('+', '').replace(',', '.') if '+' in x else '' for x in rabo['Bedrag']],
    })

    filename = splitext(basename(transactions_path))[0]

    for key, groupdf in df_ynab.groupby('Account'):
        fn = 'output/{}-{}.csv'.format(filename, key)
        print("Writing {} {} transactions".format(fn, len(groupdf)))
        groupdf.drop('Account', 1).to_csv(fn, index=0)

if __name__ == '__main__':
    convert()
