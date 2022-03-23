
import sys
import requests
from glob import glob
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from time import sleep
from tqdm import tqdm
import numpy as np

# productList = ['Bananas','Apples','Strawberries']



HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})



def scrapePricePerPound(productList,lbsDonated = 1,profitMargin = .2):
    datadict = {"Product":[],'Fair Market Price Per Pound':[], 'Basis Price Per Pound':[],
                'Pounds Donated':[], 'Deduction Expected':[]}
    
    if isinstance(lbsDonated, int) or isinstance(lbsDonated, float):
        donateList = False
    elif isinstance(lbsDonated, list):
        
        assert len(lbsDonated) == len(productList), 'List lengths do not match'
        donateList = True
        
    print('Calculating Deductions For Simulated Donations')
    for i in tqdm(range(len(productList))):
        
        p = productList[i]
        url = 'https://www.amazon.com/s?k='+p+'&i=wholefoods&ref=nb_sb_noss_1'
        
        page = requests.get(url,headers = HEADERS)
        soup = BeautifulSoup(page.content, features="lxml")
        
        try:
            l1 = [l.get_text() for l in soup.find_all('span', class_ = 'a-offscreen')]
            l2 = [l.get_text() for l in soup.find_all('span', class_ = 'a-size-base a-color-base')]



            l2 = l2[:len(l1)]
            pricefound = False
            for j in range(len(l1)):
                if 'lb' in l2[j]:
                    price = float(l1[j].replace('$',''))
                    
                    pricefound = True
                    
                    break
            if not pricefound:
                
                assert False
        except:
            #do other system
            souplist = [s.get_text() for s in soup.find_all('span', class_ = 'a-size-base a-color-secondary')]
            
            for s in souplist:
                if 'lb' in s:
                    price = s.split('/')[0].replace('$','').replace('(','')
                    price = float(price)
                    break
                elif 'Fl Oz' or 'Ounce' in s:
                    price = 16*float(s.split('/')[0].replace('$','').replace('(',''))
                    break
                    
                else:
                    price = np.nan
                    
        basisValue = round(price/(1+profitMargin),2)
        datadict['Basis Price Per Pound'].append(basisValue)
        deductionRate = basisValue + (profitMargin/2.)*basisValue
        
        if donateList:
#             print(i)
#             print(lbsDonated[i])
            
            deduction = float(lbsDonated[i])*deductionRate
            
            datadict['Pounds Donated'].append(float(lbsDonated[i]))
            
        else:
            deduction = float(lbsDonated)*deductionRate
            datadict['Pounds Donated'].append(float(lbsDonated))
            
        datadict['Deduction Expected'].append(round(deduction,2))
                    
#         print('Price of '+p+' is '+str(price)+'/lb')
        datadict['Product'].append(p)
        datadict['Fair Market Price Per Pound'].append(price)
    datadict['Product'].append('Total')
    datadict['Pounds Donated'].append(sum(datadict['Pounds Donated']))
    datadict['Deduction Expected'].append(sum(datadict['Deduction Expected']))
    datadict['Basis Price Per Pound'].append(0)
    datadict['Fair Market Price Per Pound'].append(0)
    total_deduction = datadict['Deduction Expected'][-1]
    print('Total deduction expected is '+str(total_deduction))
    print('Deduction expected using old system is '+str(1.57*datadict['Pounds Donated'][-1]))
    return datadict

# scrapePricePerPound(productList)  


if __name__ == "__main__":

	# print('Input a list of items to donate: \n Press enter between items \n When done enter Done.')

	productList = []
	lbsDonated = []

	ent=''

	while ent != 'Done':
		ent = str(input("Enter product to donate or type Done\n"))
		if ent == 'Done':
			break
		productList.append(ent)

		ent2 = float(input("Enter amount donated in lbs:\n"))
		lbsDonated.append(ent2)

	                
	# df= pd.read_csv('producelist.csv')
	# productList = list(df['Product Name'].values)
	# lbsDonated = list(50*np.random.rand(len(productList)))


	# print(isinstance)

	# datadict = 

	# print()

	# productList = ['apples']

	df = pd.DataFrame(scrapePricePerPound(productList,lbsDonated))

	print(df.head())
	# df.to_csv('deductionsimulatortest.csv',index = False)




