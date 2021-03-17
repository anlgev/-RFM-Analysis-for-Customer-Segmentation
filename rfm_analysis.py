############################################
# PROJE: RFM ile Müşteri Segmentasyonu
############################################
# Data Set Information:
# This Online Retail II data set contains all the transactions occurring for a UK-based and registered,
# non-store online retail between 01/12/2009 and 09/12/2011. The company mainly sells unique all-occasion gift-ware.
# Many customers of the company are wholesalers.

# Invoice: Invoice number. if the invoice values contain 'C' it means return
# StockCode: Product (item) code.
# Description: Product (item) name.
# Quantity: The quantities of each product (item) per Invoice.
# InvoiceDate: Invoice date and time.
# UnitPrice: Unit price.
# CustomerID: Customer number.
# Country: Country name.
############################################

import datetime as dt
import pandas as pd

pd.set_option('display.max_columns', None)

# data
df_1 = pd.read_excel('C:/Users/Asus/PycharmProjects/bootcamp/Week_3/online_retail_II.xlsx',
                    sheet_name="Year 2010-2011")
df1 = df_1.copy()

df1.head() # first five

# to delete return invoice
df1 = df1[~df1['Invoice'].str.contains('C', na=False)]

# Calculate total price
df1['TotalPrice'] = df1['Quantity'] * df1['Price']

# Looking na values and delete ttem
df1.isnull().sum()
df1.dropna(inplace=True)

# Looking some basic statistical details
df1.describe([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).T

# to find last date in data and set a date that assuming analyzed after 2 days from last date in data
df1['InvoiceDate'].max()
today = dt.datetime(2011, 12, 11)

# to create new dataframe for rfm analysis
rfm = df1.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today - date.max()).days,
                                     'Invoice': lambda num: len(num),
                                     'TotalPrice': 'sum'})

# give rename to columns
rfm.columns = ['Recency', 'Frequency', 'Monetary']

# choose the positive values
rfm = rfm[(rfm['Monetary'] > 0) & rfm['Frequency'] > 0]

# scoring metrics
rfm['RecencyScore'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
rfm['FrequencyScore'] = pd.qcut(rfm['Frequency'], 5, labels=[1, 2, 3, 4, 5])
rfm['MonetaryScore'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
rfm['RFM_SCORE'] = (rfm['RecencyScore'].astype(str) +
                    rfm['FrequencyScore'].astype(str) +
                    rfm['MonetaryScore'].astype(str))

# to create segments
seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At_Risk',
    r'[1-2]5': 'Cant_Loose',
    r'3[1-2]': 'About_to_Sleep',
    r'33': 'Need_Attention',
    r'[3-4][4-5]': 'Loyal_Customers',
    r'41': 'Promising',
    r'51': 'New_Customers',
    r'[4-5][2-3]': 'Potential_Loyalists',
    r'5[4-5]': 'Champions'
}

rfm['Segment'] = rfm['RecencyScore'].astype(str) + rfm['FrequencyScore'].astype(str)

rfm['Segment'] = rfm['Segment'].replace(seg_map, regex=True)

rfm.head()

# loogking for segments mean
df_rfm = rfm[['Segment', 'Recency', 'Frequency', 'Monetary']].groupby('Segment').\
    agg(['mean', 'count'])

# show 'Loyal_Customers' segment
rfm[rfm['Segment'] == 'Loyal_Customers'].head()
rfm[rfm['Segment'] == 'Loyal_Customers'].index


LC = pd.DataFrame()
LC['Loyal_Customers'] = rfm[rfm['Segment'] == 'Loyal_Customers'].index
LC.to_excel('Loyal_Customers.xlsx')