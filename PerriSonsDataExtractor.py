import sys
import numpy as np
import pandas as pd
from pdfminer import high_level
import requests
from json import dump
from datetime import datetime
from datetime import timedelta

local_pdf_filename = sys.argv[1]

pages = [0] # just the first page

extracted_text = high_level.extract_text(local_pdf_filename, "", pages)


invoiceNumber = int(extracted_text.split('Invoice #: ')[1].split('\n')[0])

modified_text = extracted_text.split('Page 1 of 1')[1]
modified_text = modified_text.split('SEAL')[0]
# print(modified_text)

# print(modified_text.split('\n'))
splitText = modified_text.split('\n')

def get_current_date():
    """
    Gets the current date.
    """
    today = datetime.now()
    return today.month, today.day, today.year


month, day, year = get_current_date()


##########download onion data
regionname = 'SOUTHWEST+U.S.'
producename = 'ONIONS+DRY'

url = 'https://www.marketnews.usda.gov/mnp/fv-report-retail?repType=&run=&portal=fv&locChoose=&commodityClass=&startIndex=1&type=retail&class=ALL&commodity='+str(producename)+'&region='+str(regionname)+'&organic=ALL&repDate='+str(month)+'%2F'+str(day)+'%2F'+str(year)+'&endDate=12%2F31%2F'+str(year)+'&compareLy=No&format=excel&rowDisplayMax=100000'

r = requests.get(url, allow_redirects=True, timeout=300)

onion_data = pd.read_html(r.content, header=0, parse_dates=True, index_col='Date')[0]

onion_data = onion_data[onion_data['Unit'] == 'per pound']

onion_data = onion_data[onion_data['Organic'] != 'Y']


############

while True:
    try:
        splitText.remove('')
        
    except:
        break

while True:
    try:
        splitText.remove('Brown SS')
        
    except:
        break
        
while True:
    try:
        splitText.remove('SS')
        
    except:
        break
        


produceList = []
for w in modified_text.split('\n'):
    if len(w) >20:
        produceList.append(w)

        

produce_pounds_per_bag = []
produce_grade = []
produce_size = []
produce_names = []
produce_location = []
price_per_pound = []


for w in produceList:
    v = w.split('Prod of ')[1][:2]
    produce_location.append(v)

#let's do produce name first:
for w in produceList:
    v = w.split('LB')[0][:-4]
    produce_names.append(v)
    
    variety = v.split(' Onion')[0].upper()
    try:
        price_per_pound.append(float(onion_data[onion_data['Variety'] == variety]['Weighted Avg Price'][0]
                                    ))
    except:
        print(variety)
    

#now let's do produce size
for w in produceList:
    v = w.split(' US #')[0]
    s = v.split(' ')[-1]
    produce_size.append(s)

for w in produceList:
    v = w.split(' LB')[0]
    s = v.split(' ')[-1]
    produce_pounds_per_bag.append(s)

for w in produceList:
    v = w.split('#')[1][0]
    produce_grade.append('US #'+v)
    
    
# for w in produceList:
    

quantities = []
for w in splitText:
    if 'bag' in w:
        quantities.append(int(w.split(' bag')[0]))
        


total_pounds = []
market_value = []
tax_deduction = []

for i in range(len(quantities)):
    q = quantities[i]
    p = produce_pounds_per_bag[i]
    d = price_per_pound[i]
    
    lbs = int(p)*int(q)

    total_pounds.append(lbs)
    market_value.append(lbs*d)
    tax_deduction.append(lbs*d*.5)
    
    


data = {}
data['Grade'] = produce_grade
data['Size'] = produce_size
data['Location'] = produce_location
data['Quantity (LBS)'] = total_pounds
data['Tax Deduction'] = tax_deduction
columns = produce_names
df = pd.DataFrame.from_dict(data, orient='index',
                       columns=columns)


df.to_csv('PerriSonsDonationData'+str(invoiceNumber)+'.csv')