
from clean_up import Cleanning
import pandas as pd
import numpy as np
class Full_Data(Cleanning):
    
    """
    This subclass is collecting the whole data needed in a single dataframe
    """
    def __init__(self, pricefile='price', stockfile='stock', costfile='cost', weightfile = 'weight'):
        super().__init__()
        
        self.price = pd.read_excel(pricefile+".xlsx",sheet_name='Sheet1')
        self.price = self.price.groupby('code').max()
        self.df.loc[:,'avg_price'] = self.price.loc[self.df.index,'unit_price']
        
        self.stock = pd.read_excel(stockfile+".xlsx",sheet_name='Sheet1')
        self.stock.set_index('code', inplace=True)
        self.df['stock'] = 0
        for i in self.stock.index:
            if i in self.df.index:
                self.df.loc[i,'stock'] = self.stock.loc[i,'stock']
                
        
        self.weight = pd.read_excel(weightfile+'.xlsx')
        self.weight.code = self.weight.code.astype(int)
        self.weight.set_index('code',inplace=True)
        self.df['weight'] = np.nan
        for i in self.weight.index:
            if i in self.df.index:
                self.df.loc[i,'weight'] = self.weight.loc[i,'weight']
                
    
        
        self.cost = pd.read_excel(costfile+".xlsx",sheet_name='Sheet1')
        self.cost.set_index('code',inplace=True)
        for i in self.cost.index:
            if i in self.df.index:
                self.df.loc[i,'avg_cost'] = self.cost.loc[i,'avg_cost']
    
    
    
        
        self.df.drop(self.df[self.df.name.str.contains(r'.*(كوماكس)+.*(2رول)+.*')].index, inplace= True)
        self.df = self.df[['name', 'avg_cost', 'avg_price',
                           'annual_demand','base_stock','company',
                           'order_quantity', 'stock', 'weight']]
        
        self.df.columns = ['name', 'avg_cost', 'avg_price',
                           'annual_demand','base_stock','company',
                           'MOQ', 'stock', 'weight']
        
        
        
        @staticmethod
        def transform(row):
            if row['annual_demand'] > 10000:
                return row['annual_demand'] / 12
            elif row['annual_demand'] > 6000 and row['annual_demand'] < 10000:
                return row['annual_demand'] / 14
            elif row['annual_demand'] > 3200 and row['annual_demand'] < 10000:
                return row['annual_demand'] / 17
            else:
                return row['annual_demand'] / 20
            
        self.df['order_quantity'] = self.df.apply(transform,axis=1)
        self.df = self.df
        
        
if __name__ == '__name__':
    data = Full_Data()
    print(data.df.head())
