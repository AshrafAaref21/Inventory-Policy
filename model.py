#-----------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from pyomo.opt import SolverFactory
import pyomo.environ as pyo
import pyomo
from data import Full_Data
class Inventory_Policy(Full_Data):
    """This class implements a standard Purchasing model. """

    def __init__(self, itemcode):
        super().__init__()
        """
        This sub Class Created to make an Optimizated Model for Inventory System
        """
        #self.model = None
        self.itemcode = itemcode

        company_name = self.df.loc[self.itemcode,'company']
        self.opt_df = self.df[self.df['company'] == company_name]
        
        self.car_weight = 5000000
        self.n = 1
        #self.createModel()
        

    def createModel(self):
        """Create the pyomo model given the data."""
        
        self.model = pyo.ConcreteModel()

        
        # Create sets
        self.model.i = pyo.Set(initialize=self.opt_df.index)

        
        # Create variables
        self.model.X = pyo.Var(self.model.i, initialize=0, domain=pyo.NonNegativeReals)
        X = self.model.X
        self.model.Y = pyo.Var(self.model.i, domain=pyo.Binary)
        Y = self.model.Y

        
        # Create objective
        def obj_rule(model):
            return sum((self.opt_df.loc[i,'avg_price'] - self.opt_df.loc[i,'avg_cost'])* X[i] for i in self.model.i)

        self.model.ObjF = pyo.Objective(rule = obj_rule, sense= pyo.maximize)
        
        
        # Create Constraints:
        
        # 1) Weight Capacity
        def weight_constraint(model):
            return sum(self.opt_df.loc[i,'weight']*X[i] for i in self.model.i) <= self.n*self.car_weight 
        self.model.wt_con = pyo.Constraint(rule= weight_constraint)
        
        # 2) Stock Constraint
        self.model.st_con = pyo.ConstraintList()
        for i in self.model.i:
            if self.opt_df.loc[i,'stock'] > 2 * self.opt_df.loc[i,'base_stock']:
                pass
            else:
                self.model.st_con.add(expr =
                                      X[i] + self.opt_df.loc[i,'stock'] >=
                                      self.opt_df.loc[i,'base_stock'] + self.opt_df.loc[i,'annual_demand']/50)

        
        # 2`) Stock` Constraint
        self.model.st2_con = pyo.ConstraintList()
        for i in self.model.i:
            if self.opt_df.loc[i,'stock'] > 2 * self.opt_df.loc[i,'base_stock']:
                pass
            else:
                self.model.st2_con.add(expr =
                                      X[i] + self.opt_df.loc[i,'stock'] >=
                                      self.opt_df.loc[i,'base_stock'])               
                
        
        # 3) Demand Constraint combined with minimum job order Constraint
        self.model.dd_con = pyo.ConstraintList()
        for i in self.model.i:
            if self.opt_df.loc[i,'stock'] >= self.opt_df.loc[i,'base_stock'] + self.opt_df.loc[i,'order_quantity']:
                self.model.dd_con.add(expr = X[i] == 0)
            else:
                self.model.dd_con.add(
                    expr = X[i] + self.opt_df.loc[i,'stock'] <= max(
                        self.opt_df.loc[i,'stock']+50,self.opt_df.loc[i,'base_stock'] + self.opt_df.loc[i,'order_quantity']))
                
                
        # 4) Inventory Balance         
        self.model.in_con = pyo.ConstraintList()
        for i in self.model.i:
            if self.opt_df.loc[i,'stock'] > 2 * self.opt_df.loc[i,'base_stock']:
                self.model.st_con.add(expr = X[i] == 0)
        
        # 4) Minimum job Order Constraint        
        def min_order_constraint(model,i):
            return X[i] >= 50* Y[i]
        self.model.jb_con = pyo.Constraint(self.model.i, rule = min_order_constraint)
        
        # 5) Linking Constraint
        def linking_constraint(model,i):
            return X[i] <= 10000 * Y[i]
        self.model.lk_con = pyo.Constraint(self.model.i, rule= linking_constraint)
                

            
    @property
    def releaseWeightConstraint(self):
        """This Method Created to Release Weight Constraint"""
        self.model.del_component(self.model.wt_con)
        
    @property
    def releaseStockConstraint(self):
        """This Method Created to Release Weight Constraint"""
        self.model.del_component(self.model.st_con)
    @property
    def releaseStock2Constraint(self):
        """This Method Created to Release Weight Constraint"""
        self.model.del_component(self.model.st2_con)
    @property
    def releaseDemandConstraint(self):
        """This Method Created to Release Weight Constraint"""
        self.model.del_component(self.model.dd_con)
        
    @property
    def releaseMinimumConstraint(self):
        """This Method Created to Release Weight Constraint"""
        self.model.del_component(self.model.jb_con)
        
    @property
    def releaseInventoryBalanceConstraint(self):
        """This Method Created to Release Weight Constraint"""
        self.model.del_component(self.model.in_con)
        
        
    def SetCarWeight(self,weight):
        """Car Weight Setter Method"""
        self.car_weight = weight
        
    def SetNumCars(self,num):
        """Number of Used Trucks Setter Method"""
        self.n = num
        
        
    def solve(self):
        """Solve the model."""
        import logging
        solver = SolverFactory('cplex_direct')

        results = solver.solve(self.model, tee=True, keepfiles=False, options_string="mip_tolerances_integrality=1e-9 mip_tolerances_mipgap=0")
        
        if (results.solver.status != pyomo.opt.SolverStatus.ok):
            logging.warning('Check solver not ok?')
            
        if (results.solver.termination_condition != pyomo.opt.TerminationCondition.optimal):  
            
            logging.warning('Check solver optimality?') 

    
if __name__ == '__main__':
    
    item = int(input("Kindly, Input the item code that got the the alert: "))
    sp = Inventory_Policy(item) 
    sp.createModel()
    solver = SolverFactory('cplex_direct')
    results = solver.solve(sp.model)
    if sp.model.ObjF() < 1:
        print("You can't Order only one Car to satisfy the inventory demand\nWe gonna use 2 cars instead")
        sp = Inventory_Policy(item)
        sp.createModel()
        sp.releaseWeightConstraint
        
        results = solver.solve(sp.model)
    print('\n\n---------------------------------')
    print('\nTotal Cost: ', np.round(sp.model.ObjF(),2),"LE")
    print('\n\n---------------------------------')

    n=0
    for i in sp.model.i:
        print(f'{sp.opt_df.index[n]} => {int(np.ceil(sp.model.X[i]()))} Box')
        n+=1
    print('\n\n---------------------------------')

    print('\nTotal Weight ==>',sum(sp.opt_df.loc[i,'weight']*sp.model.X[i]() for i in sp.model.i)/1000,"KG")
    print('\n#NOTE THAT:\n\tCar Capacity ==>',sp.car_weight/1000,'KG')


# ------------------------------------------------------------------------------------------------------------
