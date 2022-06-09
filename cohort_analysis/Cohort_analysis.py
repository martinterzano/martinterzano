# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 15:50:39 2021

@author: Martin Terzano
"""


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import date
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import urllib
from sqlalchemy import create_engine
import warnings
from operator import attrgetter
import matplotlib.colors as mcolors

#-----------------------------------------------------------------


#ETL

"""I import the dataframe containing all the sales in the last 2 years. It has cancelled, paid and pending sales. 
    I the filter the dataframe:
        1) to have only rows from sales that have been paid.
        2) to have only sales with an identified customer so I delete customers without ID.
"""

Ventas= pd.read_excel(r"C:\Users\...\VentasSinMelt.xlsx", encoding = "ISO-8859-1")

Ventas=Ventas[(Ventas['status_pago']=="paga") & (Ventas['id_cliente_unificado']!="0")]

Ventas.info()
Ventas.describe()

def eliminapunto (x):
    return(x.replace('.0',''))


#-----------------------------------------------------------------


# I create new features including number of orders per client

n_orders = Ventas.groupby(['id_cliente_unificado'])['id_op'].nunique()
mult_orders_perc = np.sum(n_orders > 1) / Ventas['id_cliente_unificado'].nunique()
print(f'{100 * mult_orders_perc:.2f}% of customers ordered more than once.')


#I start plotting

ax = sns.distplot(n_orders, kde=False, hist=True)
ax.set(title='Distribution of number of orders per customer',
       xlabel='# of orders', 
       ylabel='# of customers');


#I eliminate duplicates so that operations are not repeated

Ventas = Ventas[['id_cliente_unificado', 'id_op', 'fecha_op']].drop_duplicates()

#Since we have operations of the same date but with different times, they are not eliminated. We correct this.

Ventas['fecha_op']=Ventas['fecha_op'].dt.strftime('%d/%m/%Y')
Ventas['fecha_op']=pd.to_datetime(Ventas['fecha_op'],format= "%d/%m/%Y")

#We remove duplicates again

Ventas = Ventas[['id_cliente_unificado', 'id_op', 'fecha_op']].drop_duplicates()

#I create the "Month" and "Cohort" column. The last one is the month of the client's first operation.

Ventas['order_month'] = Ventas['fecha_op'].dt.to_period('M')
Ventas['cohort'] = Ventas.groupby('id_cliente_unificado')['fecha_op'] \
                 .transform('min') \
                 .dt.to_period('M') 

#Remove null values
                 
Ventas = Ventas[Ventas['cohort'].notnull()]


#I group by "Cohort" and "order month", and count the number of customers in each group. Then we add the calculation period number.

Ventas_cohort = Ventas.groupby(['cohort', 'order_month']) \
              .agg(n_customers=('id_cliente_unificado', 'nunique')) \
              .reset_index(drop=False)
Ventas_cohort['period_number'] = (Ventas_cohort.order_month - Ventas_cohort.cohort).apply(attrgetter('n'))


#Now that we have all the data let's pivot it

cohort_pivot = Ventas_cohort.pivot_table(index = 'cohort',
                                     columns = 'period_number',
                                     values = 'n_customers')

#Now let's create a retention matrix. That is, we compare the number of customers in each period against the initial period.

cohort_size = cohort_pivot.iloc[:,0]
retention_matrix = cohort_pivot.divide(cohort_size, axis = 0)

#I plot with a heatmap

with sns.axes_style("white"):
    fig, ax = plt.subplots(1, 2, figsize=(12, 8), sharey=True, gridspec_kw={'width_ratios': [1, 11]})
    
    # retention matrix
    sns.heatmap(retention_matrix, 
                mask=retention_matrix.isnull(), 
                annot=True, 
                fmt='.0%', 
                cmap='RdYlGn', 
                ax=ax[1])
    ax[1].set_title('Monthly Cohorts: User Retention', fontsize=16)
    ax[1].set(xlabel='# of periods',
              ylabel='')

    # cohort size
    cohort_size_df = pd.DataFrame(cohort_size).rename(columns={0: 'cohort_size'})
    white_cmap = mcolors.ListedColormap(['white'])
    sns.heatmap(cohort_size_df, 
                annot=True, 
                cbar=False, 
                fmt='g', 
                cmap=white_cmap, 
                ax=ax[0])

    fig.tight_layout()
 

 #-----------------------------------------------------------------
#I export the retention matrix


retention_matrix.to_excel(r'C:\Users\...\retention_matrix.xlsx')

