# Crypto.com Rewards Tracker

> **_DISCLAIMER:_**  this repository contains a tool that I use for my own calculations. It's not guaranteed to work as expected or work at all. **Use it at your own risk**.

## Description
This tool was created to parse Crypto.com app CSV export and calculate the fiat income received on a set year.

## Why
In many countries, cryptocurrencies are taxable assets and have to be declared. While there are dedicated tools for the job, like [Cointracking](https://cointracking.info), they offer very limited free tiers.

This tool tries to be a very simple free alternative that can be used for income tracking **when no permutations are involved**. If you just need to track the fiat value of your stake/earn/cashback/reimbrusment rewards **at the moment they were given to you**, this tool might work for you. If, on the other hand, you have to track any kind of buy/sell operations, you should use a dedicated tracker.

## How to use

### Quick note on exchangerates

Crypto.com seem to provide some transactions like the referral rewards always in USD, regardless of your main currency (specified via `TARGET_CURRENCY`). For accurately reporting, this tool uses [Exchangerates](https://exchangeratesapi.io/) to get the right currency conversion rate at the moment of any trasnsaction reported in a different currency than your main one. 
This repository comes with an api key for the free tier that might hit the requests limit for the month (1000 req/month) if many people use it. 

Therefore, you can try to run the script as it comes but it's recommended to create a free account and use your own key to avoid any rate limiting.

---

Export all your crypto wallet transactions for the tax year on the Crypto.com App menu and save the csv file somewhere on your computer

Clone this repository and replace the API key:
```bash
git clone https://github.com/rubasace/cdc-rewards-tracker.git
cd cdc-rewards-tracker
//Recomended to replace the API key at this point
//You can also change your base currency if it isn't EUR

```
Install the dependencies and run the script:
```bash
pip install -r requirements.txt
python cdcTracker.py
```

You'll be prompted for the file location. Select your previously exported report and wait for the tool to finish.

It will show you an aggregated of all taxable transactions as well as any possible reversals:

```commandline
REPORT INFO
Taxable transactions:
                                                                          Converted Amount      
                                                                                       sum count
Year Transaction Kind          Transaction Description Converted Currency                       
2021 crypto_earn_interest_paid Crypto Earn             EUR                              **     4
     mco_stake_reward          CRO Stake Rewards       EUR                              **    44
     referral_bonus            Referral Bonus Reward   EUR                              **     4
     referral_card_cashback    Card Cashback           EUR                              **   539
     referral_gift             Sign-up Bonus Unlocked  EUR                              **     1
     reimbursement             Card Rebate: Netflix    EUR                              **    10
                               Card Rebate: Spotify    EUR                              **     9
Taxable transactions total: 9999
Discountable transactions:
                                                                             Converted Amount      
                                                                                          sum count
Year Transaction Kind       Transaction Description       Converted Currency                       
2021 card_cashback_reverted Card Cashback Reversal        EUR                              **    11
     reimbursement_reverted Card Rebate Reversal: Netflix EUR                              **     1
Discountable transactions total: 29
```

And, finally, it will show the total income:

```commandline
Total income: **** EUR
```

## Optional configuration

Some constants on the script can be changed to tweak the behaviour:

| Name | Default         | Description                                                                                                                                                                                                                                                          |  |
| ---- |-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| -------- |
| TARGET_CURRENCY | `EUR`           | The base currency of your CDC account. Changing it to something other than `EUR` might hit the exchange API restrictions (only allows to convert from EUR on the frie tier and some workarounds are already in place).                                               | &nbsp; |
| LOGGING_LEVEL | `logging.INFO`  | You can get extra information printed by changing the `LOGGING_LEVEL` variable to `logging.DEBUG`.                                                                                                                                                                   | &nbsp; |
| EXCHANGE_API_KEY | a free tier one | You can provide your own key to avoid potential request limiting                                                                                                                                                                                                     | &nbsp; |
| EXCHANGE_API_FREE_TIER | `True  `          | You can set this to `False` if you have a paid API key. This will allow you to convert from and to any currency. It will also disable the workaround that calculates the the rate from any currency (`X`) to `EUR` by getting the `EUR -> X` ratio and inverting it. | &nbsp; |


## Requirements
* Python 3.4 or greater
* A Crypto.com App transaction CSV report
* (Recommended) your own [exchangerates](https://exchangeratesapi.io/) API key