from os.path import basename, splitext
import pandas as pd
import click

@click.command()
@click.argument('input_path', type=click.Path(exists=True))
def convert(input_path):
    EXAMPLE = click.format_filename(input_path)
    df = pd.read_csv(EXAMPLE, encoding = 'latin1')

    pd.set_option("display.max_columns",101)

    df_ynab = pd.DataFrame({
        'Account': df['IBAN/BBAN'],
        'Date': [x.strftime('%Y-%m-%d') for x in pd.to_datetime(df['Datum'])],
        'Payee': [x if not pd.isnull(x) else '' for x in df['Naam tegenpartij']],
        'Category': ['' for x in df['IBAN/BBAN']],
        'Memo': df['Omschrijving-1'],
        'Outflow': [x.replace('-', '').replace(',', '.') if '-' in x else '' for x in df['Bedrag']],
        'Inflow': [x.replace('+', '').replace(',', '.') if '+' in x else '' for x in df['Bedrag']],
    })

    filename = splitext(basename(EXAMPLE))[0]

    for key, groupdf in df_ynab.groupby('Account'):
        fn = 'output/{}-{}.csv'.format(filename, key)
        print("Writing {} {} transactions".format(fn, len(groupdf)))
        groupdf.drop('Account', 1).to_csv(fn, index=0)

if __name__ == '__main__':
    convert()
