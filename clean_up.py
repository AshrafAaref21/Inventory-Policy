import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')


class Cleanning:
    """
    This Class is doing Data Clean up from sales Excel File to fit in Inventory model
    """
    def __init__(self,salesFile= 'total_sales', nsheet = 'Sheet1'):
        """Read in the excel data."""
        
        if salesFile == 'total_sales':
            self.df = pd.read_excel(salesFile+'.xlsx', sheet_name='Data')
            self.df = self.df['date code name unit quantity avg_price unit_cost'.split()]
            self.df['month'] = self.df.date.dt.month
            self.df['year'] = self.df.date.dt.year
            self.df['code'] = self.df['code'].astype(int)
            self.df['quantity'] = self.df['quantity'].astype(float)
            self.df['avg_price'] = self.df['avg_price'].astype(float)
            self.df['unit_cost'] = self.df['unit_cost'].astype(float)

            self.itemcode_duplication
            self.data_preprocessing
            
            
        else:
            self.df = pd.read_excel(salesFile+'.xlsx', sheet_name=nsheet)
    
    @property
    def itemcode_duplication(self):
        '''
        Cleanning Items Duplications
        '''
        df = self.df
        df_comax_4kg_30cm = df[df.name.str.contains(r'.*(كوماكس)+.*(جامبو)+.*(4)+.*')]
        df.loc[df_comax_4kg_30cm.index , 'code'] = df_comax_4kg_30cm.code.max()
        df.loc[df_comax_4kg_30cm.index , 'name'] = df_comax_4kg_30cm.iloc[-1,2]

        df_comax_5kg = df[df.name.str.contains(r'.*(كوماكس)+.*(جامبو)+.*(5)+.*')]
        width = ['35','40']
        for x in width:
            df.loc[df_comax_5kg[df_comax_5kg.code.astype(str).str.contains('30421'+x)].index,'code'] = df_comax_5kg[
                df_comax_5kg.code.astype(str).str.contains('30421'+x)].code.max()
            df.loc[df_comax_5kg[df_comax_5kg.code.astype(str).str.contains('30421'+x)].index,'name'] = df_comax_5kg[
                df_comax_5kg.code.astype(str).str.contains('30421'+x)].iloc[-1,2]

        df_comax_7kg = df[df.name.str.contains(r'.*(كوماكس)+.*(جامبو)+.*(7)+.*')]
        width = ['30','35','40']
        for x in width:
            df.loc[df_comax_7kg[df_comax_7kg.code.astype(str).str.contains('30421'+x)].index,'code'] = df_comax_7kg[
                df_comax_7kg.code.astype(str).str.contains('30421'+x)].code.max()
            df.loc[df_comax_7kg[df_comax_7kg.code.astype(str).str.contains('30421'+x)].index,'name'] = df_comax_7kg[
                df_comax_7kg.code.astype(str).str.contains('30421'+x)].iloc[-1,2]

        df_comax_2roll = df[df.name.str.contains(r'.*(كوماكس)+.*(2رول)+.*')]

        for x in width:
            df.loc[df_comax_2roll[df_comax_2roll.code.astype(str).str.contains('30421'+x)].index,'code'] = df_comax_2roll[
                df_comax_2roll.code.astype(str).str.contains('30421'+x)].code.max()
            df.loc[df_comax_2roll[df_comax_2roll.code.astype(str).str.contains('30421'+x)].index,'name'] = df_comax_2roll[
                df_comax_2roll.code.astype(str).str.contains('30421'+x)].iloc[-1,2]

        df_himax = df[df.name.str.contains('ها')]
        for x in width:
            df.loc[df_himax[df_himax.code.astype(str).str.contains('30421'+x)].index,'code'] = df_himax[
            df_himax.code.astype(str).str.contains('30421'+x)].code.max()
            df.loc[df_himax[df_himax.code.astype(str).str.contains('30421'+x)].index,'name'] = df_himax[
            df_himax.code.astype(str).str.contains('30421'+x)].iloc[-1,2]

        
        df_corn_jambo = df[df.name.str.contains(r'.*(CORN)+.*(جامبو)+.*(5)+.*')]
        
        df_corn_jambo_35 = df_corn_jambo[df_corn_jambo['name'].str.contains('35')]
        df.loc[df_corn_jambo_35.index,'code'] = df_corn_jambo_35.code.max()
        df.loc[df_corn_jambo_35.index,'name'] = df_corn_jambo_35.iloc[-1,2]
        
        df_corn_jambo_40 = df_corn_jambo[df_corn_jambo['name'].str.contains('40')]
        df.loc[df_corn_jambo_40.index,'code'] = df_corn_jambo_40.code.max()
        df.loc[df_corn_jambo_40.index,'name'] = df_corn_jambo_40.iloc[-1,2]
        
        
        df.loc[df[df.name.str.contains(r'(30)+.*(جرين)+.*')].index,'code'] = df[
            df.name.str.contains(r'(30)+.*(جرين)+.*')].code.max()
        df.loc[df[df.name.str.contains(r'(30)+.*(جرين)+.*')].index,'name'] = df[
            df.name.str.contains(r'(30)+.*(جرين)+.*')].iloc[-1,2]
               
        df.loc[df[df.name.str.contains(r'(35)+.*(جرين)+.*')].index,'code'] = df[
            df.name.str.contains(r'(35)+.*(جرين)+.*')].code.max()
        df.loc[df[df.name.str.contains(r'(35)+.*(جرين)+.*')].index,'name'] = df[
            df.name.str.contains(r'(35)+.*(جرين)+.*')].iloc[-1,2]
        
           
   
    @property
    def data_preprocessing(self):
        '''
        Proccessing The Data
        '''
        df = self.df

        #Grouping THE DataFrame to get the True sales for each SKU in each month
        df_grouped = df.groupby(['code','name','year','month']).agg(
            avg_cost=('unit_cost', np.max),
            avg_price=('avg_price', np.max),
            quantity=('quantity', np.sum)).reset_index().set_index('code').sort_index().sort_values([ 'year', 'month'])
        
        
        #Treat the Sales Quantity To get the True Demand Quantity
        for i in df_grouped.index.value_counts().index:
            avg_demand = df_grouped.loc[i,'quantity'].mean()
            df_grouped.loc[i,'quantity'] = pd.Series(df_grouped.loc[i,'quantity']).apply(
                lambda x: avg_demand if x < avg_demand else x).values
            
            
        #Grouping the DataFrame to get the requried data to allocate inventory policy
        df_grouped = df_grouped.reset_index().groupby(['code','name']).agg(
            avg_cost=('avg_cost', np.max),
            avg_price=('avg_price', np.max),
            mean_quantity=('quantity', np.mean),
            sum_quantity=('quantity', np.sum),
            std_quantity=('quantity', np.std),
            n_sample= ('quantity', len)).reset_index().set_index('code').sort_index()
        df_grouped['annual_demand'] = df_grouped['mean_quantity'] *12
        
        
        #Calculating the K-Factor (CSL)
        from scipy.stats import norm
        def k_score(row):
            if row['annual_demand'] > 8000:
                return norm.ppf(0.95)
            elif row['annual_demand'] > 4000 and row['annual_demand'] < 8000:
                return norm.ppf(0.85)
            else:
                return norm.ppf(0.75)
        df_grouped['k'] = df_grouped.apply(k_score,axis=1)
        #Calculating The Base Stock
        df_grouped['base_stock'] = df_grouped['annual_demand']*7/365 +df_grouped['std_quantity']*np.sqrt(
            12*7/365) * df_grouped['k']
        
        
        #Adding the Company Name to the DataFrame
        company_dict = {
            'shams': ['كوماكس', 'هاى ماكس'],
            'masr' : ['جرين باور','OH', 'تمساح'],
            'cairo' : ['باور راب', 'King'],
            'arab' : ['CORN', 'lemon', 'Lemon', 'عباد الشمس'],
            'imported' : ['ماكسى', 'FRESH']
        }
        df_grouped['company'] = np.nan
        for i in company_dict:
            for j in company_dict[i]:
                df_grouped.loc[df_grouped[df_grouped['name'].str.contains(j)].index,'company'] = i
                
                
        #Calculating The Optimum Order Quantity
        C_t =  12253
        h = 0.35
        # Fill zero cost values with average cost
        df_grouped.loc[df_grouped[df_grouped['avg_cost'] == 0].index,'avg_cost'] = df_grouped['avg_cost'].mean()
        df_grouped['order_quantity'] = np.sqrt(2*C_t*df_grouped['annual_demand']/(df_grouped['avg_cost']*h))
        
        df_grouped = df_grouped.dropna()
        df_grouped['order_quantity'] = pd.Series(np.round(df_grouped['order_quantity'])).astype(int)
        df_grouped['base_stock'] = pd.Series(np.round(df_grouped['base_stock'])).astype(int)
        
        self.df = df_grouped.sort_index().sort_values(['company','annual_demand'],axis=0,ascending=False)
        # Removing Old items
        self.df.drop([304213559,304214050,304213075],inplace=True)        
        
    
    def save_to_excel(self, directory = os.getcwd() , filename = 'base.xlsx'): # will save it to the cwd
        '''
        Saving The Cleanned DataFrame To excel file
        
        '''
        if directory[-1] != "\\":
            directory += "\\"
            
        if filename[len(filename)-5:len(filename)] != '.xlsx':
            if filename[len(filename)-4:len(filename)] =='.csv':
                filename = filename[:len(filename)-4] +'.xlsx'
            filename+= '.xlsx'
            
        self.df[self.df['company']!='imported'].to_excel(directory+filename, sheet_name= 'Sheet1')
    
#     def __repr__(self):
#         return f"{self.df.head(1)}"
        

# if __name__ == '__main__':
    
#     data = Cleanning()
#     chainging The directory
#     data.save_to_excel()
