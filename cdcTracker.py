from tkinter import filedialog as fd
import sys
import logging
import pandas
import requests

# CONFIGURABLE
TARGET_CURRENCY = 'EUR'
LOGGING_LEVEL = logging.INFO
# REPLACE BY YOUR OWN ONE FROM exchangeratesapi.io
EXCHANGE_API_KEY = '175a058876653ce278038b91a504374a'
EXCHANGE_API_FREE_TIER = True

# Convenience columns
YEAR_COLUMN = "Year"
MONTH_COLUMN = "Month"
DAY_COLUMN = "Day"
CONVERTED_AMOUNT = "Converted Amount"
CONVERTED_CURRENCY = "Converted Currency"

# Required columns
TIMESTAMP_COLUMN = 'Timestamp (UTC)'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
NATIVE_CURRENCY_COLUMN = 'Native Currency'
NATIVE_AMOUNT_COLUMN = 'Native Amount'
TRANSACTION_DESCRIPTION_COLUMN = 'Transaction Description'
TRANSACTION_KIND_COLUMN = 'Transaction Kind'

# TODO store as structure indicating type (taxable/reversal/ignored)
# Transaction kinds
CASHBACK_KIND = 'referral_card_cashback'
CASHBACK_REVERTED_KIND = 'card_cashback_reverted'
CARD_FULL_CASHBACK_KIND = 'reimbursement'
CARD_FULL_CASHBACK_REVERTED_KIND = 'reimbursement_reverted'
CARD_TOP_UP_KIND = 'card_top_up'
CRYPTO_DEPOSIT_KIND = 'crypto_deposit'
EARN_INTEREST_PAID_KIND = 'crypto_earn_interest_paid'
EARN_PROGRAM_CREATED_KIND = 'crypto_earn_program_created'
EARN_PROGRAM_WITHDRAWN_KIND = 'crypto_earn_program_withdrawn'
CRYPTO_EXCHANGE_KIND = 'crypto_exchange'
CRYPTO_WITHDRAWAL = 'crypto_withdrawal'
DUST_CONVERSION_KIND = 'dust_conversion_credited'
LOCKUP_LOCK_KIND = 'lockup_lock'
LOCKUP_UPGRADE_KIND = 'lockup_upgrade'
STAKE_REWARD_KIND = 'mco_stake_reward'
REFERRAL_BONUS_KIND = 'referral_bonus'
REFERRAL_GIFT_KIND = 'referral_gift'
SUPERCHARGER_DEPOSIT_KIND = 'supercharger_deposit'
SUPERCHARGER_WITHDRAWAL_KIND = 'supercharger_withdrawal'
CRYPTO_PURCHASE_KIND = 'viban_purchase'

TAXABLE_TRANSACTIONS = [CASHBACK_KIND, CARD_FULL_CASHBACK_KIND, EARN_INTEREST_PAID_KIND, STAKE_REWARD_KIND,
                        REFERRAL_BONUS_KIND, REFERRAL_GIFT_KIND]
REVERSALS_TRANSACTIONS = [CASHBACK_REVERTED_KIND, CARD_FULL_CASHBACK_REVERTED_KIND]

logger = logging.getLogger()
logger.setLevel(LOGGING_LEVEL)
consoleHandler = logging.StreamHandler(sys.stdout)
logger.addHandler(consoleHandler)


def prompt_for_file():
    return fd.askopenfilename(filetypes=[('CSV files', ["*.csv"])])


def validate_csv(data_frame):
    required_columns = {TIMESTAMP_COLUMN, NATIVE_CURRENCY_COLUMN, NATIVE_AMOUNT_COLUMN, TRANSACTION_KIND_COLUMN,
                        TRANSACTION_DESCRIPTION_COLUMN}
    fieldnames = data_frame.columns
    for column in required_columns:
        if column not in fieldnames:
            logger.debug('Column %s not found in headers', column)
            raise Exception("File has an invalid format. Make sure you've imported the right file.")


def append_date_info(data_frame):
    date = pandas.to_datetime(data_frame[TIMESTAMP_COLUMN], format=TIMESTAMP_FORMAT)
    data_frame[YEAR_COLUMN] = date.dt.year
    data_frame[MONTH_COLUMN] = date.dt.month
    data_frame[DAY_COLUMN] = date.dt.day


def get_conversion_rate(from_currency, to_currency, day):
    query_params = {
        'access_key': EXCHANGE_API_KEY,
        'base': from_currency,
        'symbols': to_currency
    }
    url = "http://api.exchangeratesapi.io/v1/{}".format(day)
    response = requests.get(url, params=query_params)
    if response.status_code >= 300:
        logger.error('Couldn\'t retrieve conversion rate\n{}'.format(response.json()))
        sys.exit(1)
    return response.json()['rates'][to_currency]


def convert_amount(amount, from_currency, timestamp):
    if TARGET_CURRENCY == from_currency:
        return amount
    logger.debug('Converting %d from %s to %s', amount, from_currency, TARGET_CURRENCY)
    # Done this way cause the API only allows to use EUR as the base currency on the free tier
    if not EXCHANGE_API_FREE_TIER:
        return amount * get_conversion_rate(from_currency, TARGET_CURRENCY, timestamp.split()[0])
    elif 'EUR' == TARGET_CURRENCY:
        return amount / get_conversion_rate(TARGET_CURRENCY, from_currency, timestamp.split()[0])
    raise Exception('Cannot convert from {} to {} without a paid account'.format(from_currency, TARGET_CURRENCY))


def append_converted_amount(data_frame):
    data_frame[CONVERTED_AMOUNT] = pandas.Series(
        map(convert_amount, data_frame[NATIVE_AMOUNT_COLUMN], data_frame[NATIVE_CURRENCY_COLUMN],
            data_frame[TIMESTAMP_COLUMN]))
    data_frame[CONVERTED_CURRENCY] = TARGET_CURRENCY


def query_by_transaction_type(data_frame, transaction_types):
    query = "`{}` in [{}]".format(TRANSACTION_KIND_COLUMN, str(transaction_types).strip('[]'))
    return data_frame.query(query)


if __name__ == '__main__':
    file_path = prompt_for_file()
    logger.debug('Opening file: %s', file_path)
    df = pandas.read_csv(file_path)
    validate_csv(df)
    append_date_info(df)
    append_converted_amount(df)
    logger.debug('\nProcessed transactions:\n%s', df.to_string())
    amount_by_kind = df.groupby(
        [YEAR_COLUMN, TRANSACTION_KIND_COLUMN, TRANSACTION_DESCRIPTION_COLUMN, CONVERTED_CURRENCY]).agg(
        {CONVERTED_AMOUNT: ['sum', 'count']})
    logger.debug('Grouped transactions:\n%s', amount_by_kind.to_string())
    taxable = query_by_transaction_type(amount_by_kind, TAXABLE_TRANSACTIONS)
    reversals = query_by_transaction_type(amount_by_kind, REVERSALS_TRANSACTIONS)
    taxable_total = taxable[CONVERTED_AMOUNT]['sum'].sum()
    reversals_total = reversals[CONVERTED_AMOUNT]['sum'].sum()
    total_income = taxable_total - reversals_total

    logger.info('REPORT INFO\n'
                 'Taxable transactions:\n'
                 '%s\n'
                 'Taxable transactions total: %d\n'
                 'Reversal transactions:\n'
                 '%s\n'
                 'Reversal transactions total: %d\n'
                 'Total income: %d %s', taxable.to_string(), taxable_total, reversals.to_string(), reversals_total, total_income, TARGET_CURRENCY)
