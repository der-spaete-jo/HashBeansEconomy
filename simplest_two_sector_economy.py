'''
Created on 24.11.2016
HashBeansEconomy/simplest_two_sector_economy.py
Copyright Johannes Katzer, 2016
'''

from random import randrange, choice
from math import floor

from init_params import *
from OutputHandler import Historian

INITIAL_ECONOMY_DATA = [TMAX, NUMBER_OF_CONSUMERS, NUMBER_OF_HASH_FIRMS, NUMBER_OF_BEAN_FIRMS, CAP_UNIT_PRICE_HASH, CAP_UNIT_PRICE_BEAN]
INITIAL_FIRM_DATA = [INIT_MONEY, INIT_CAP, PER_CAP_COSTS, FIX_COSTS, QUADRATIC_COEFFICIENT, LINEAR_COEFFICIENT, MONEY_HOLDING_RATE, DIVIDEND_RATE]
INITIAL_CONSUMER_DATA = [SUBSISTENCE_NEED_HASH, SUBSISTENCE_NEED_BEAN, RELATIVE_PREFERENCE_HASH, ENDOW]

class EconomyController():
    def __init__(self, t_max, K_0, J_0, N_0, p_H, p_B, init_consumer_data, init_firm_data):
        self.t_max = t_max
        self.K = []
        self.J = []
        self.N = []
        self.K_0 = K_0
        self.J_0 = J_0
        self.N_0 = N_0
        self.p_H = p_H
        self.p_B = p_B
        self.init_consumer_data = init_consumer_data
        self.init_hashfirm_data = init_firm_data + [self.p_H]
        self.init_beanfirm_data = init_firm_data + [self.p_B]        
        self.Div_per_capita = 0          
                
        self.consumer_id = 101       
        self.hash_firm_id = 11
        self.bean_firm_id = 11
        
        self.historian = Historian()
        self.historian.initializeEconomyHistory()      
        self.initializeAgents()  
        
    def initializeAgents(self):
        for k in range(self.K_0):
            consumer = Consumer(*self.init_consumer_data)
            self.registerAgent(consumer)
        for j in range(self.J_0):
            hash_firm = HashFirm(*self.init_hashfirm_data)
            self.registerAgent(hash_firm)
        for n in range(self.N_0):
            bean_firm = BeanFirm(*self.init_beanfirm_data)
            self.registerAgent(bean_firm)
                        
    def registerAgent(self, agent):        
        if  isinstance(agent, HashFirm):
            agent.name = "HF00{0}".format(self.hash_firm_id)            
            self.J.append(agent)            
            self.hash_firm_id += 1
            print("A hash firm was launched")
            print(agent)
            agent.historian = self.historian
            self.historian.initializeFirmHistory(agent)
        elif isinstance(agent, BeanFirm):
            agent.name = "BF00{0}".format(self.bean_firm_id)
            self.N.append(agent)
            self.bean_firm_id += 1
            print("A bean firm was launched")
            print(agent)
            agent.historian = self.historian
            self.historian.initializeFirmHistory(agent)
        elif isinstance(agent, Consumer):
            agent.name = "C00{0}".format(self.consumer_id)
            self.K.append(agent)
            self.consumer_id += 1
            print("A consumer was born")
            print(agent)
            agent.historian = self.historian
            self.historian.initializeConsumerHistory(agent)        
            
    def unregisterAgent(self, agent):
        if isinstance(agent, HashFirm):
            self.J.remove(agent)  
            print("A hash firm went bankrupt")
            print(agent)      
        elif isinstance(agent, BeanFirm):
            self.N.remove(agent)
            print("A bean firm went bankrupt")
            print(agent) 
        elif isinstance(agent, Consumer):
            self.K.remove(agent)
            print("A consumer died")
            print(agent) 
        del agent
        
    def priceDiscoveryProcess(self, hash_supply, bean_supply, solvent_consumers, stocked_firms, T, k):
        """ Consumers reveal lowest price and chose their demand """
        try: 
            min_p_h = min([offer[0] for offer in hash_supply.values()])
            competitive_hash_firms = [f for f in self.J if f.getSupplyOffer()[0] == min_p_h]
        except ValueError: # "min() arg is an empty sequence" is raised if min is called on empty list
            min_p_h = -1
            competitive_hash_firms = []
        try: 
            min_p_b = min([offer[0] for offer in bean_supply.values()])
            competitive_bean_firms = [f for f in self.N if f.getSupplyOffer()[0] == min_p_b] 
        except ValueError:
            min_p_b = -1
            competitive_bean_firms = [] 
      
        iter_consumers = solvent_consumers    
        for c in iter_consumers: 
            if c.getResidualIncome() > 0 and c.updateShoppingList(min_p_h, min_p_b):                
                try:
                    hash_idx = randrange(0,len(competitive_hash_firms))
                    hash_supplier = competitive_hash_firms[hash_idx]
                    hash_supplier.updateDemandQueue(c)
                except ValueError:
                    pass 
                try:
                    bean_idx = randrange(0,len(competitive_bean_firms))                
                    bean_supplier = competitive_bean_firms[bean_idx]
                    bean_supplier.updateDemandQueue(c)
                except ValueError:
                    pass               
            else:# if c.updateShoppingList() == False:
                solvent_consumers.remove(c)
            
        """ firms serve the consumers in their pipelines """
        for f in competitive_hash_firms: 
            residual_offer = f.processDemandQueue()
            if residual_offer[1] == 0:
                try:
                    stocked_firms.remove(f)
                    del(hash_supply[f])
                except ValueError:
                    print('ERROR: {0} was not removed from stocked firms in the price discovery round {1} in period {2}'.format(f, T, k))                
            elif residual_offer[1] > 0:
                hash_supply[f] = residual_offer
                
        for f in competitive_bean_firms: 
            residual_offer = f.processDemandQueue()
            if residual_offer[1] == 0:
                try:
                    stocked_firms.remove(f)
                    del(bean_supply[f])
                except ValueError:
                    print('ERROR: {0} was not removed from stocked firms in the price discovery round {1} in period {2}'.format(f, T, k))                
            elif residual_offer[1] > 0:
                bean_supply[f] = residual_offer
                
        return hash_supply, bean_supply, solvent_consumers, stocked_firms
        
    def run(self):
        
        for T in range(self.t_max):
            print("=====================")
            print("starting period {0}".format(T))
            self.historian.reportValue("history_file", "no_of_consumers", len(self.K))
            self.historian.reportValue("history_file", "no_of_hash_firms", len(self.J))
            self.historian.reportValue("history_file", "no_of_bean_firms", len(self.N))
            self.historian.reportValue("history_file", "per_capita_dividend", self.Div_per_capita)
            firms = self.J + self.N
            consumers = self.K

            """ calculate Income """
            for consumer in consumers:
                consumer.updateInc(T, self.Div_per_capita)
                consumer.historian.reportValue(consumer.getName(), "income", consumer.Inc)
                
            """ prepare supply side """            
            hash_supply = {}
            bean_supply = {}
            for j in self.J:
                j.updateSupplyOffer()
                hash_supply[j] = j.getSupplyOffer()
            for n in self.N:
                n.updateSupplyOffer()
                bean_supply[n] = n.getSupplyOffer() 
                               
            """ trade """            
            solvent_consumers = list(consumers)
            stocked_firms = list(firms)
            k = 0
            while solvent_consumers and stocked_firms: # there is supply left and solvent consumers exist
                hash_supply, bean_supply, solvent_consumers, stocked_firms = self.priceDiscoveryProcess(hash_supply, bean_supply, solvent_consumers, stocked_firms, T, k)
                k += 1
                if k > len(self.K)*(len(self.J)+len(self.N)):
                    print("ERROR: Price discovery process produced infinite loop and was canceled")
                    break
                
            """ prepare agents for next period and delete failed agents
                    - consumers die from starvation 
                    - consumers save money and eat up hash n beans that they bought
                    - firms allocate profits and calculate dividends for next period 
                    - firms with negative net worth leave the market
                    """
            for consumer in consumers:
                if consumer.getResidualHashNeeds() > 0 or consumer.getResidualBeanNeeds() > 0:
                    self.unregisterAgent(consumer)
                consumer.finishPeriod()

            Div_sum = 0
            for firm in firms:
                firm.finishPeriod()
                Div = firm.getDiv()
                Div_sum += Div
                if firm.getNetWorth() < 0:
                    self.unregisterAgent(firm)
            self.Div_per_capita = Div_sum/len(self.N)
            
        for arg in ["money", "capacity", "dividend", "production", "sales", "revenue", "total_costs", "profit", "income", "expenditures", "savings", "hash", "bean"]:   
            self.historian.mergerFiles(arg)
        for args in [["unit_price", "hash"], ["unit_price", "bean"], ["production", "hash"], ["production", "bean"]]:
            self.historian.mergerFiles(*args)
            
        self.historian.prepareData(self.t_max)
        #self.historian.prepareGraphs(self.t_max)    
        
        print("Terminated!")
       
class Firm():
    def __init__(self, Money_0, Cap_0, f, F, S, R, m, d):
        """ program organization """
        self.name = None    # set by EconomyController on registration
        self.historian = None
        """ parameters """
        self.f = f      # should have names that mean something
        self.F = F      
        self.S = S
        self.R = R             
        self.m = m
        self.d = d 
        self.Cap_unit_price = None      # will be set if we now the type of the firm...        
        """ choice variables """ 
        self.Money = Money_0            # period T Liquidity, fixed in T=0, then chosen in allocateProfit()
        self.Cap = Cap_0                # period T Capacity, fixed in T=0, then chosen in allocateProfit()
        self.Div = 0                    # Dividend to be paid in T+1, updated by allocateProfit()
        
        self.unit_price = 1             # period T unit price for the good, chosen in updateSupplyOffer()
        self.production = self.Cap      # period T quantity produced of the good, chosen in updateSupplyOffer() 
        """ intern calculations """
        self.stock = self.production    # period T round X residual quantity of the good (left over after some price discovery rounds)
        self.demand_queue = []          # period T Round X demand queue 
        self.Cap_old = 0                # period T-1 production capacities  
        
        """ derived variables """ 
        self.FCosts =  f*self.Cap + F   
        self.NetWorth = 0   
        
        self.quantity_sold = 0          # period T quantity sold
        self.TCosts = 0                 # period T-1 total costs
        self.revenue = 0                # period T-1 revenues
        self.profit = 0                 # period T-1 profit
        
        
    """ getter, setter and updater methods """  
    def getName(self):
        return self.name
    def setName(self, new_name):
        self.name = new_name
    def updateFCosts(self):
        self.FCosts =  self.f*self.Cap + self.F
    def getNetWorth(self): 
        return self.NetWorth   
    def updateNetWorth(self):
        self.NetWorth = self.Money + self.Cap/self.Cap_unit_price
                
    def getUnitPrice(self):
        return self.unit_price
    def setUnitPrice(self, new_price):
        self.unit_price = new_price    
    def getProduction(self):
        return self.production
    def setProduction(self, quantity):
        self.production = quantity
    def getStock(self):
        return self.stock
    def setStock(self, new_quantity):
        self.stock = new_quantity
    
    def getSupplyOffer(self): 
        return (self.unit_price, self.stock)
    def getDemandQueue(self):
        return self.demand_queue
    def updateDemandQueue(self, demander):
        if demander == -1:
            self.demand_queue = []
            return 
        self.demand_queue.append(demander)    
    def getDiv(self):
        return self.Div
    def setDiv(self, new_dividend):
        self.Div = new_dividend 
        
    """ methods that actually do stuff """ 
    def updateSupplyOffer(self):                    # called once each period to set price and production for this period
        increment = randrange(1,101)*self.unit_price/100    # see Axelrod
        if self.quantity_sold == self.Cap_old:
            self.unit_price += increment
        else:
            self.unit_price += -increment           
        self.unit_price = max(0.1, floor(100*self.unit_price)/100) # p > 0 and p only has 2 digits after komma (x,yz)
        self.production = self.Cap                  # always produce as much as possible  
        self.stock = self.production                # fill inventory with produced goods 
        # and because updateSupplyOffer() is called every period on every agent once, it is convenient to pull out the data:
        self.historian.reportValue(self.getName(), "money", self.Money)     
        self.historian.reportValue(self.getName(), "capacity", self.Cap)
        self.historian.reportValue(self.getName(), "dividend", self.Div)
        
        self.historian.reportValue(self.getName(), "unit_price", self.unit_price)     
        self.historian.reportValue(self.getName(), "production", self.production)   
        
        
    def allocateProfit(self):   
        m = self.m
        d = self.d        
        if self.profit>0 and self.quantity_sold == self.Cap:
            self.Money = (1-d)*(self.Money + m*self.profit)
            self.Cap = self.Cap + (1-m)*self.profit/self.Cap_unit_price
            self.Div = d*(self.Money + m*self.profit)
        elif self.profit>0 and self.quantity_sold < self.Cap:
            self.Money = (1-d)*(self.Money + self.profit)
            self.Cap = self.Cap
            self.Div = d*(self.Money + self.profit)
        else:   #if self.profit < 0:
            if self.Money + self.profit >= 0:
                ind = 1
            else:
                ind = 0
            self.Money = ind*(self.Money + self.profit)
            self.Cap = self.Cap + (1-ind)*(self.Money + self.profit)/self.Cap_unit_price
            self.Div = 0
                     
    
    def funcTCosts(self, Q):
        return self.S*(Q**2)+self.R*Q+self.FCosts
       
    def finishPeriod(self):
        self.Cap_old = self.Cap     #save old cap for calc of next supply offer        
        self.quantity_sold = self.production - self.stock
        self.revenue = self.unit_price*self.quantity_sold
        self.TCosts = self.funcTCosts(self.production)
        self.profit = self.revenue - self.TCosts
        
        self.historian.reportValue(self.getName(), "sales", self.quantity_sold)
        self.historian.reportValue(self.getName(), "revenue", self.revenue)     
        self.historian.reportValue(self.getName(), "total_costs", self.TCosts)
        self.historian.reportValue(self.getName(), "profit", self.profit)
        
        self.allocateProfit()
        self.profit = 0   
        self.stock = 0
        self.updateFCosts()
        self.updateNetWorth()
    
    def processDemandQueue(self):       # why use this if/else construction?
        pipeline = self.getDemandQueue()
        if self.stock > sum([c.getDemand(self.product) for c in pipeline]): 
            # all consumers get their full demand served
            for c in pipeline:
                goods = c.getDemand(self.product)
                self.setStock(self.getStock() - goods)
                c.makePurchase(self.product, goods, self.unit_price)       
            residual_offer = self.getSupplyOffer()
        else: # firm faces excess demand
            while self.stock > 0:
                c = choice(pipeline)
                goods = min(c.getDemand(self.product), self.stock)
                self.setStock(self.getStock() - goods)
                c.makePurchase(self.product, goods, self.unit_price)
                pipeline.remove(c)                 
            residual_offer = self.getSupplyOffer()
        self.updateDemandQueue(-1)
        return residual_offer
    
    def __repr__(self):
        return self.name
    def __str__(self):
        strng = "Firm {0}, Money: {1} EUR, Capacity: {2} units, Net Worth: {3} EUR,".format(self.name, self.Money, self.Cap, self.NetWorth)
        return strng
    
class HashFirm(Firm):
    def __init__(self, Money_0, Cap_0, f, F, S, R, m, d, p_H):
        super().__init__(Money_0, Cap_0, f, F, S, R, m, d)
        self.product = "hash"
        self.Cap_unit_price = p_H
        self.updateNetWorth()    

class BeanFirm(Firm):
    def __init__(self, Money_0, Cap_0, f, F, S, R, m, d, p_B):
        super().__init__(Money_0, Cap_0, f, F, S, R, m, d)
        self.product = "bean"
        self.Cap_unit_price = p_B
        self.updateNetWorth()
        
class Consumer():
    def __init__(self, h_sn, b_sn, a, Endow):   
        """ program organization """   
        self.name = None
        self.historian = None
        """ parameters """
        self.h_sn = h_sn
        self.b_sn = b_sn
        self.a = a
        self.Endow = Endow
        """ choice variables """
        self.h_d = None         # period T Round X demand for hash
        self.b_d = None         # period T Round X demand for beans
        """ intern calculations """        
        self.Exp = 0            # period T accumulated Expenditures
        self.Inc = 0            # period T Income
        self.Sav = 0            # period T Savings
        self.h = 0              # actual purchases of hash in T
        self.b = 0              # actual purchases of beans in T
        
        #self.h_star = self.h_sn # period T residual subsistence need of hash (after some price discovery rounds)
        #self.b_star = self.b_sn # period T residual subsistence need of beans (after some price discovery rounds)
        #self.Inc_star = 0      # calculated on the flow, by "getResidualIncome()". Period T residual Income (after some price discovery rounds)        
    
    def getName(self):
        return self.name
    def setName(self, new_name):
        self.name = new_name
            
    def getHashNeeds(self):
        return self.h_sn
    def getBeanNeeds(self):
        return self.b_sn
    
    def getHashPurchases(self):
        return self.h
    def getBeanPurchases(self):
        return self.b
    def updateHashPurchases(self, quantity):
        self.h += quantity    
    def updateBeanPurchases(self, quantity):
        self.b += quantity            
    
    def getResidualHashNeeds(self):
        return self.h_sn - self.h
    def getResidualBeanNeeds(self):
        return self.b_sn - self.b 
    def getHashDemand(self):
        return self.h_d 
    def getBeanDemand(self):
        return self.b_d
    def getDemand(self, product):
        if product == "hash":
            return self.h_d
        elif product == "bean":
            return self.b_d
    #def setResidualHashNeeds(self, new_residual):
    #    self.h_star = new_residual  
    #def setResidualBeanNeeds(self, new_residual):
    #    self.b_star = new_residual  
    def setHashDemand(self, quantity):
        self.h_d = quantity
    def setBeanDemand(self, quantity):
        self.b_d = quantity    
  
    def getExp(self):
        return self.Exp    
    def updateExp(self, expediture):
        self.Exp += expediture      
    def updateSav(self):
        self.Sav = self.Inc - self.Exp
    def updateInc(self, period, Div_per_capita):
        self.Inc = self.Sav + self.Endow[period] + Div_per_capita        
    
    def getResidualIncome(self):
        return self.Inc - self.Exp

        
    """ methods that actually do stuff """   
    def updateShoppingList(self, min_p_h, min_p_b):
        if min_p_h < 0: # there are no more offers in the hash market
            if self.getResidualHashNeeds() > 0 or min_p_b*self.getResidualBeanNeeds() > self.getResidualIncome():
                return False
            else:
                self.setHashDemand(0)
                self.setBeanDemand(self.getResidualIncome()/min_p_b)
        elif min_p_b < 0: # there are no more offers in the bean market
            if self.getResidualBeanNeeds() > 0 or min_p_h*self.getResidualHashNeeds() > self.getResidualIncome():
                return False
            else:
                self.setHashDemand(self.getResidualIncome()/min_p_h)
                self.setBeanDemand(0)
        else:
            if min_p_h * self.getResidualHashNeeds() + min_p_b * self.getResidualBeanNeeds() > self.getResidualIncome():
                return False
            else:
                optimal_hash_demand = (1-self.a)*self.getResidualHashNeeds() + self.a*(self.getResidualIncome() - min_p_b*self.getResidualBeanNeeds())/min_p_h
                optimal_bean_demand = self.a*self.getResidualBeanNeeds() + (1-self.a)*(self.getResidualIncome() - min_p_h*self.getResidualHashNeeds())/min_p_b
                self.setHashDemand(max(0, optimal_hash_demand))
                self.setBeanDemand(max(0, optimal_bean_demand))
                if self.getBeanDemand() == 0:
                    self.setHashDemand(self.getResidualIncome()/min_p_h)
                if self.getHashDemand() == 0:
                    self.setBeanDemand(self.getResidualIncome()/min_p_b)
        return True
    
    def makePurchase(self, product, quantity, price):
        if product == "hash":
            self.updateHashPurchases(quantity)
            self.updateExp(quantity*price)
            #self.setResidualHashNeeds(self.getResidualHashNeeds() - quantity)
        elif product == "bean":
            self.updateBeanPurchases(quantity)
            self.updateExp(quantity*price)
            #self.setResidualBeanNeeds(self.getResidualBeanNeeds() - quantity)

    def finishPeriod(self):
        self.updateSav()
        self.historian.reportValue(self.getName(), "expenditures", self.Exp)
        self.historian.reportValue(self.getName(), "savings", self.Sav)
        
        self.historian.reportValue(self.getName(), "hash", self.h)
        self.historian.reportValue(self.getName(), "bean", self.b)
        
        self.h = 0
        self.b = 0
        #self.h_star = self.h_sn
        #self.b_star = self.b_sn 
        self.Exp = 0       
    
    def funcUtility(self, h , b):
        return (h-self.h_sn)**self.a * (b-self.b_sn)**(1-self.a)    
    
    def __repr__(self):
        repr_string = ";".join([str(v) for v in [self.name, self.h_sn, self.b_sn, self.a]])
        repr_string = repr_string + ";[" + ",".join([str(v) for v in self.Endow]) + "]"
        return repr_string
    def __str__(self):
        strng = "Consumer {x}, Income: {0} EUR, Hash: {1} units, Bean: {2} units".format(self.Inc, self.h, self.b, x=self.name)
        return strng

def createAgent(economy_controller, repr_string):
    inform = repr_string.split(";")
    if inform[0].startswith("C"):
        data = [int(v) for v in inform[1:]]
        data.append()
        new_agent = Consumer(*data) 
        economy_controller.registerAgent(new_agent)
        
invisible_hand = EconomyController(*INITIAL_ECONOMY_DATA, INITIAL_CONSUMER_DATA, INITIAL_FIRM_DATA)
invisible_hand.run()  