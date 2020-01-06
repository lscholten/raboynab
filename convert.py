from os.path import basename, splitext
import pandas as pd
import click


def convert_credit_account(df):
    num_entries = len(df)
    return pd.DataFrame({
        'Account': [f"{name}-{number}" for name, number in zip(df['Productnaam'], df['Creditcard Nummer'])],
        'Date': [x.strftime('%Y-%m-%d') for x in pd.to_datetime(df['Datum'])],
        'Payee': ['Creditcard'] * num_entries,
        'Category': [''] * num_entries,
        'Memo': df['Omschrijving'],
        'Outflow': [-x if x < 0 else '' for x in df['Bedrag']],
        'Inflow': [x if x >= 0 else '' for x in df['Bedrag']],
    })


def convert_regular_account(df):
    return pd.DataFrame({
        'Account': df['IBAN/BBAN'],
        'Date': [x.strftime('%Y-%m-%d') for x in pd.to_datetime(df['Datum'])],
        'Payee': [x if not pd.isnull(x) else '' for x in df['Naam tegenpartij']],
        'Category': ['' for x in df['IBAN/BBAN']],
        'Memo': df['Omschrijving-1'],
        'Outflow': [x.replace('-', '').replace(',', '.') if '-' in x else '' for x in df['Bedrag']],
        'Inflow': [x.replace('+', '').replace(',', '.') if '+' in x else '' for x in df['Bedrag']],
    })



def get_converter(rabo_df):
    if 'Creditcard Nummer' in list(rabo_df.columns):
        return convert_credit_account
    return convert_regular_account


def filter_date(ynab_df, start_date):
    return ynab_df[pd.to_datetime(ynab_df['Date']) >= start_date]

@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--start_date', type=click.DateTime(formats=["%Y-%m-%d"]), default="1970-01-01")
def convert(input_path, start_date):
    transactions_path = click.format_filename(input_path)
    rabo_df = pd.read_csv(transactions_path, encoding='latin1')

    converter = get_converter(rabo_df)
    df_ynab = filter_date(converter(rabo_df), start_date)

    filename = splitext(basename(transactions_path))[0]
    for key, groupdf in df_ynab.groupby('Account'):
        fn = 'output/{}-{}.csv'.format(filename, key)
        print("Writing {} {} transactions".format(fn, len(groupdf)))
        groupdf.drop('Account', 1).to_csv(fn, index=0)


if __name__ == '__main__':
    convert()
