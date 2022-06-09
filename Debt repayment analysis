# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 12:03:27 2020

@author: Martin Terzano
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import date

#--------------------------------------------------------------------------#
"""I import two dataframes:
    dfcred contains all the loans granted by the company. 
    df contains all the past and future installments belonging those loans with their respective payment amounts and payment date.
"""

dfcred=pd.read_excel(r"C:\Users\...\Archivo creditos historico.xlsx")
df=pd.read_excel(r"C:\Users\...\Archivo cuotas historico.xlsx")

#--------------------------------------------------------------------------#

today = pd.to_datetime(date.today(),format='%Y/%m/%d')

#--------------------------------------------------------------------------#


#df Transformation

df.info()
df['f_vencimiento']= pd.to_datetime(df['f_vencimiento'])
df['f_pago']= pd.to_datetime(df['f_pago'].replace("-",None))
df['f_pago']= pd.to_datetime(df['f_pago'])
df['Dias_mora']= df['f_pago'] - df['f_vencimiento']
df['Dias_mora'] = pd.to_numeric(df['Dias_mora'].dt.days, downcast='integer')

Dias_mora= df['Dias_mora']

result = []
for date in Dias_mora:
    
    if date <= 30:
        result.append('0-30')
    elif date <= 90:
        result.append('31-90')
    elif date <= 180:
        result.append('91-180')
    elif date <= 365:
        result.append('181-365')
    elif date >= 365:
        result.append('>365')
    else:
        result.append('0-30')
        
df['ESD'] = result

#--------------------------------------------------------------------------#


#dfcred Transformation

dfcred.info()

dfcred['FECHA EMISION']= pd.to_datetime(dfcred['f_originacion'])

def firstdayofmonth(any_day):
    return(any_day.replace(day=1))
    
dfcred['mes_alta']= dfcred['FECHA EMISION'].apply(firstdayofmonth)


#--------------------------------------------------------------------------#


#I create dffinal by joining the modified df and dfcred to add the original loan date


dffinal = df.merge(dfcred,how='left',left_on= 'id_boleto', right_on= 'idboleto')
dffinal.info()
def punto (x):
    return(x.replace(',','.'))

dffinal.info()


#--------------------------------------------------------------------------#


"""I import the data I need to build the unpivoted dataframe of all situations, amount balances and month of registration for each calculation date
"""

vinesd= pd.read_excel(r"C:\Users\...\Vintage DEF ESD.xlsx")
vinsc= pd.read_excel(r"C:\Users\...\Vintage DEF SC.xlsx")

vinesd.info()
vinsc.info()

"""I melt the files in order to have all the data organized in rows. First I do the pivot by ESD (debtor's financial status) and then by Capital Balance.
I create a common code by registration date and calculation date to be able to join the two generated tables.
"""

vinesd_unpivoted = pd.melt(vinesd,id_vars=['Mes Alta'], var_name='Mes Calculo', value_name='ESD')
vinesd_unpivoted
vinesd_unpivoted['codigo'] = vinesd_unpivoted['Mes Alta'].astype(str)+vinesd_unpivoted['Mes Calculo'].astype(str)
vinesd_unpivoted.info()

vinsc_unpivoted = pd.melt(vinsc,id_vars=['Mes Alta'], var_name='Mes Calculo', value_name='SaldoCap')
vinsc_unpivoted
vinsc_unpivoted['codigo'] = vinsc_unpivoted['Mes Alta'].astype(str)+vinsc_unpivoted['Mes Calculo'].astype(str)
vinsc_unpivoted.info()
vinsc_unpivoted.rename(columns={'Mes Alta': 'Mes Alta1', 'Mes Calculo': 'Mes Calculo1'}, inplace=True)

"""I concatenate the tables so that the following variables remain in the same row: ESD, Month High, Month Calculation and Capital Balance. 
With this I already have the data ready to create the vintage.
"""

vinfinal = pd.concat([vinsc_unpivoted,vinesd_unpivoted], axis=1,join='inner')
vinfinal['ESD'] = pd.Categorical(vinfinal['ESD'], categories=['0-30', '31-90', '91-180','181-365', '>365'])


vinfinal.info()
vinfinal["Mes Alta"]= vinfinal["Mes Alta"].dt.strftime('%Y-%m-%d')

#--------------------------------------------------------------------------#


#Creating Vintage

#I create a table to have the originated capital variable per month.

Originacion= dfcred.groupby('mes_alta',as_index=False).agg({'monto_documentos/cuotas_total':sum})
Originacion["mes_alta"]= Originacion["mes_alta"].dt.strftime('%Y-%m-%d')
Originacion["mes_alta"]= Originacion["mes_alta"].astype(str)
Originacion.info()

"""
Excel creation with the different calculation Month tabs
Import the Excel Writer to be able to incorporate info in each Tab
"""

from pandas import ExcelWriter

#I establish an initial calculation month from which I am going to create the tabs and an object with the address of the resulting file to be exported

Mes_calculo = datetime.strptime("01-07-2018","%d-%m-%Y")
w = ExcelWriter(r"C:\Users\...\Vintage Final - USD.xlsx")

"""
#I do the for while loop. What I am looking for is to create a pivot table for each month of calculation where all the Vintage data is.
#I create the table for a specific calculation month, work it, save it in a tab and then add a month to the calculation month to iterate over the months.
"""

while Mes_calculo < today:  
    df=pd.pivot_table(data=vinfinal[(vinfinal['Mes Calculo']==Mes_calculo) & (vinfinal['Mes Alta1']<Mes_calculo)], values= "SaldoCap", index="Mes Alta", columns= "ESD", aggfunc=sum, fill_value= 0,dropna=False,margins=True,margins_name="Total")
    df.reset_index(level=0, inplace=True)
    df[""]= "" 
    df["Mora > 90"]= df["91-180"]+df["181-365"]+df[">365"]
    df["Mora > 180"]= df["181-365"]+df[">365"]
    df=df.merge(Originacion,how="left", left_on="Mes Alta", right_on="mes_alta")
    df = df[['Mes Alta','monto_documentos/cuotas_total', '0-30', '31-90', '91-180','181-365', '>365', 'Total', '', 'Mora > 90', 'Mora > 180', 'mes_alta']].drop(columns="mes_alta").rename(columns={"monto_documentos/cuotas_total":"Originado"})
    df["% Mora > 90"]= df.apply(lambda x : (x["Mora > 90"]/x["Originado"]) if pd.notnull(x["Originado"]) else 0,axis=1)
    df["% Mora > 180"]=df.apply(lambda x : (x["Mora > 180"]/x["Originado"]) if pd.notnull(x["Originado"]) else 0,axis=1)
    df["% Mora > 90"] = pd.Series(["{0:.2f}%".format(val * 100) for val in df["% Mora > 90"]], index = df.index)
    df["% Mora > 180"] = pd.Series(["{0:.2f}%".format(val * 100) for val in df["% Mora > 180"]], index = df.index)
    df.to_excel(w, 'Mes' + str(pd.to_datetime(Mes_calculo,format = "%d-%m-%Y").year) + str(pd.to_datetime(Mes_calculo,format = "%d-%m-%Y").month),index=False)
    Mes_calculo = pd.Timestamp(Mes_calculo) + pd.DateOffset(months=1)
w.save()


#I export the unpivoted file to Excel

vinfinal.to_excel(r'C:\Users\...\Vintage Data - USD.xlsx', index = False)

