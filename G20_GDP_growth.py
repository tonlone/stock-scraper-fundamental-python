from pandas_datareader import wb
import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf
import pandas as pd
import numpy as np

#1. Load packages, and download data.
#For the GDP data, we are using the World Bank data from the pandas_datareader package.
gdp_variables = wb.search('gdp.*capita.*const')

#print(gdp_variables)
wb_data = wb.download(indicator='NY.GDP.PCAP.KD', 
                      country=['AR', 'ID', 'AU', 'CA', 'DE', 'IT', 'JP',
                               'FR', 'GB', 'MX', 'KR', 'BR', 'ZA', 'IN',
                               'SA', 'CN', 'US', 'TR'], 
                      start=2015, 
                      end=2023)

#For the mapping, I’ve created a dictionary with the country name and corresponding ETF.
#We would use ETFs for performance evaluation as they are denominated in US $, which hedges the currency devaluation risk.

# Map the countries to their corresponding ETFs.
etfs = {'Argentina': 'ARGT', 'Indonesia': 'EIDO', 'Australia': 'EWA',
        'Canada': 'EWC', 'Germany': 'EWG', 'Italy': 'EWI', 'Japan': 'EWJ',
        'France': 'EWQ', 'United Kingdom': 'EWU', 'Mexico': 'EWW',
         'Korea, Rep.': 'EWY', 'Brazil': 'EWZ', 'South Africa': 'FLZA',
         'India': 'INDA', 'Saudi Arabia': 'KSA', 'China': 'MCHI',
         'United States': 'SPY', 'Turkiye': 'TUR'}

wb_data = wb_data.reset_index()

wb_data['etf_code'] = wb_data['country'].map(etfs)

wb_data = wb_data.set_index(['year', 'country']).unstack().stack()

#print(wb_data)

# 3. Calculate GDP growth and rank cross-sectionally, then calculate the year-over-year rank difference and again rank cross-sectionally.

wb_data['pct_chg'] = wb_data.groupby(level=1)['NY.GDP.PCAP.KD']\
                            .transform(lambda x: x.pct_change())

wb_data['rank'] = wb_data.groupby(level=0)['pct_chg']\
                         .transform(lambda x: x.rank(ascending=False))

wb_data['rank_diff'] = wb_data.groupby(level=1)['rank']\
                              .transform(lambda x: x.diff())

wb_data['rank_by_rank_diff'] = wb_data.groupby(level=0)['rank_diff']\
                               .transform(lambda x: x.rank(ascending=True))

#print(wb_data)



#First, we calculate the year-over-year growth rate in GDP per capita.
#Next, we rank the countries cross-sectionally for each year based on the GDP growth.
#Next, we calculate the country, year-over-year difference in the cross-sectional rank.
#Finally, we calculate a new cross-sectional rank based on that difference. Basically, the country which have climbed the most in the GDP growth rank would be the number one here.

# 4. Visualize all countries by GDP growth for better understanding.
for i in range(2018, 2023):
    
    selected = wb_data.xs(pd.to_datetime(i, format='%Y').strftime('%Y'),
                          level=0)['pct_chg'].sort_values(ascending=False)
    
    selected.plot(kind='bar', figsize=(16,4))
    
    plt.title(f'{i} Year GDP Growth')
    
    plt.gcf().autofmt_xdate()
    
 #   plt.show()

#5. Grab the top 1 country for the given year and compare to SPY.
filtered_df = wb_data[(wb_data['rank_by_rank_diff']==1)]

filtered_df = filtered_df.reset_index(level=1)

filtered_df.index = pd.to_datetime(filtered_df.index) + pd.offsets.YearEnd() + pd.DateOffset(1)

filtered_df = filtered_df.reset_index().set_index(['year', 'etf_code']).unstack().stack()

dates = filtered_df.index.get_level_values('year').unique().tolist()

fixed_dates ={}

for d in dates:
    
    fixed_dates[d.strftime('%Y-%m-%d')] = filtered_df.xs(d, level=0).index.tolist()
    
fixed_dates

# 6. Compare performance with SPY for 2022 pick — other country.
end_date = '2023-07-01'

start_date = '2022-01-01'

#etfs = {'Argentina': 'ARGT', 'Indonesia': 'EIDO', 'Australia': 'EWA',
#        'Canada': 'EWC', 'Germany': 'EWG', 'Italy': 'EWI', 'Japan': 'EWJ',
#        'France': 'EWQ', 'United Kingdom': 'EWU', 'Mexico': 'EWW',
#         'Korea, Rep.': 'EWY', 'Brazil': 'EWZ', 'South Africa': 'FLZA',
#         'India': 'INDA', 'Saudi Arabia': 'KSA', 'China': 'MCHI',
#         'United States': 'SPY', 'Turkiye': 'TUR'}
otherFund = "MCHI"

prices_df = yf.download(['SPY', otherFund],
                        start_date,
                        end_date).stack()

prices_df['return'] = prices_df.groupby(level=1)['Adj Close']\
                               .transform(lambda x: x.pct_change())

comparison_df = np.exp(np.log1p(prices_df['return'].unstack()).cumsum())

comparison_df.plot(figsize=(16,6))

plt.title(f'SPY / {otherFund} Performance Comparison')

plt.ylabel('Return')

plt.show()