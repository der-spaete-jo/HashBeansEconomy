'''
Created on 24.11.2016
HashBeansEconomy/OutputHandler.py
Copyright Johannes Katzer, 2016
'''

import matplotlib.pyplot as plt
import datetime
import os

class Historian():  # encapsulates full information over past periods s.t. agents have no access
    def __init__(self):
        """ merger files """
        """ the EconomyController """
        # his files are already in a merged state, cause he is solo w.r.t. agent_type       
        """ firms """
        self.history_file_money = None
        self.history_file_capacity = None
        self.history_file_dividend = None
        self.history_file_unit_price_hash = None
        self.history_file_unit_price_bean = None
        self.history_file_production_hash = None
        self.history_file_production_bean = None
        self.history_file_sales = None
        self.history_file_revenue = None
        self.history_file_total_costs = None
        self.history_file_profit = None        
        """ consumers """
        self.history_file_income = None
        self.history_file_expenditures = None
        self.history_file_savings = None
        self.history_file_hash = None
        self.history_file_bean = None
        """ program organization """
        self.wd_local_path = None        
        self.history_files={}        
        self.createHistory()
        """ time series'es resulting from the data """
        self.no_of_agents_time_series = {}  
        self.sector_wide_mean_price_time_series = {}
        self.sector_wide_production_time_series = {}
        
    def initializeFirmHistory(self, agent):
        self.createHistoryFile(agent.getName() + "_money" + ".txt")          # Given my liquidity,
        self.createHistoryFile(agent.getName() + "_capacity" + ".txt")       # capacity
        self.createHistoryFile(agent.getName() + "_dividend" + ".txt")       # and the dividend (that I paid) in period T
                    
        self.createHistoryFile(agent.getName() + "_unit_price" + ".txt")     # I set this unit price
        self.createHistoryFile(agent.getName() + "_production" + ".txt")     # and this level of production.
      
        self.createHistoryFile(agent.getName() + "_sales" + ".txt")          # That generates at the end of period T
        self.createHistoryFile(agent.getName() + "_revenue" + ".txt")        # this revenue
        self.createHistoryFile(agent.getName() + "_total_costs" + ".txt")    #
        self.createHistoryFile(agent.getName() + "_profit" + ".txt")         # and this profit
    def initializeConsumerHistory(self, agent):        
        self.createHistoryFile(agent.getName() + "_income" + ".txt")         # Given my income in period T
        self.createHistoryFile(agent.getName() + "_expenditures" + ".txt")   # 
        self.createHistoryFile(agent.getName() + "_savings" + ".txt") 
        self.createHistoryFile(agent.getName() + "_hash" + ".txt")   
        self.createHistoryFile(agent.getName() + "_bean" + ".txt") 
    def initializeEconomyHistory(self, agent):        
        self.createHistoryFile("history_file_" + "_no_of_consumers" + ".txt")
        self.createHistoryFile("history_file_" + "_no_of_hash_firms" + ".txt")
        self.createHistoryFile("history_file_" + "_no_of_bean_firms" + ".txt")
        self.createHistoryFile("history_file_" + "_per_capita_dividend" + ".txt")
            
    def createHistory(self):
        date_string = str(datetime.datetime.now())
        date_string = date_string.split(".")[0]
        date_string = date_string.translate({ord(v) : None for v in ' -:'})
        name = "HashBeansEcon" + date_string
        os.mkdir(name)
        os.chdir(name)
        self.wd_local_path = name
        
    def createHistoryFile(self, file_name):
        f = open(file_name, "w")
        self.history_files[file_name] = f
        f.close()
    
    def reportValue(self, agent_reporting, type_reported, value_reported):
        f = open(agent_reporting + "_" + type_reported + ".txt", "a")
        f.write(str(value_reported) + "; ")
        f.close()
    
    def mergerFiles(self, variable_type, hb=None):
        if hb:
            filename = "history_file_" + str(variable_type) + "_" + hb + ".txt"
            if hb == "hash":                
                ident = "HF0"
            elif hb == "bean":
                ident = "BF0"
        else:
            filename = "history_file_" + variable_type + ".txt"
            ident = "" 
        open(filename, "w").close()
        for key in self.history_files.keys():
            if key.split(".")[0].endswith(variable_type) and key.startswith(ident):
                with open(key, "r") as f:
                    data = f.read()
                    with open(filename, "a") as merg_f:
                        merg_f.write(data + "\n")
      
    def prepareData(self, max_period):  # more encapsulation possible? repeated similar code...
        # prepare number of agents statistics
        no_of_agents_time_series = {}
        for agent_type in ["consumers", "hash_firms", "bean_firms"]:
            filename = "history_file_" + "no_of_" + agent_type + ".txt"
            with open(filename, "r") as f:
                line_list = f.read().split(";")
                line_list.pop() # the last entry in line_list is ' ', because the lines in .txt files end with '; '.
                no_of_agents_time_series[agent_type] = line_list
        self.no_of_agents_time_series = no_of_agents_time_series   
         
        # prepare sector-wide mean price
        for sector in ["hash", "bean"]:
            filename = "history_file_" + "unit_price_" + sector + ".txt"
                             
            with open(filename, "r") as f:
                lines = f.read().splitlines()
                lines = [line.split(";") for line in lines]
            mean_price_time_series = []
            for T in range(max_period):
                per_period_price_sum = 0
                for line in lines:
                    try:
                        per_period_price_sum += float(line[T])
                    except (ValueError, IndexError) as e:
                        #print("ERROR: {0} is missing in aggregate statistics of {1}".format(line[T], str(type_to_show)))
                        pass # this agent died before period T
                per_period_mean_price = per_period_price_sum/int(self.no_of_agents_time_series[sector + "_firms"][T])  
                mean_price_time_series.append(per_period_mean_price)
            self.sector_wide_mean_price_time_series[sector] = mean_price_time_series
            
        # prepare sector-wide aggregate production measured in units
        for sector in ["hash", "bean"]:
            filename = "history_file_" + "production_" + sector + ".txt"
                             
            with open(filename, "r") as f:
                lines = f.read().splitlines()
                lines = [line.split(";") for line in lines]
            production_time_series = []
            for T in range(max_period):
                per_period_production_sum = 0
                for line in lines:
                    try:
                        per_period_production_sum += float(line[T])
                    except (ValueError, IndexError) as e:
                        #print("ERROR: {0} is missing in aggregate statistics of {1}".format(line[T], str(type_to_show)))
                        pass # this agent died before period T  
                production_time_series.append(per_period_production_sum)
            self.sector_wide_production_time_series[sector] = production_time_series
        
        # generate weights
        # prepare sector-wide weighted mean price (weighted with the share of firms production in total production of the sector)
        # prepare global price index 
        # prepare GDP time series
        
    def prepareGraphs(self, max_period):   # more encapsulation needed, repeated similar code!
        # prepare number of agents graph
        fig = plt.figure()
        fig.suptitle("Number of agents", fontsize=14, fontweight='bold')
        graph = fig.add_subplot(111)
        line_1 = graph.plot(range(max_period), self.no_of_agents_time_series["consumers"], "r-")
        line_2 = graph.plot(range(max_period), self.no_of_agents_time_series["hash_firms"], "b-")
        line_3 = graph.plot(range(max_period), self.no_of_agents_time_series["bean_firms"], "g-")   
        #plt.legend((line_1,line_2,line_3), ('consumer', 'hash firms', 'bean firms'))     
        max_values = [int(max(l)) for l in list(self.no_of_agents_time_series.values())]
        graph.axis([0, max_period, 0, 1.2*max(max_values)])
        graph.set_ylabel("number")
        graph.set_xlabel("period") 
        # prepare sector-wide mean price graph
        fig_1 = plt.figure()
        fig_1.suptitle("Sector-wide mean prices", fontsize=14, fontweight='bold')
        graph = fig_1.add_subplot(111)
        graph.plot(range(max_period), self.sector_wide_mean_price_time_series["hash"], "b-")
        graph.plot(range(max_period), self.sector_wide_mean_price_time_series["bean"], "g-")        
        max_values = [int(max(l)) for l in list(self.sector_wide_mean_price_time_series.values())]
        graph.axis([0, max_period, 0, 1.2*max(max_values)])
        graph.set_ylabel("EUR")
        graph.set_xlabel("period")
        # prepare sector-wide production graph
        fig_2 = plt.figure()
        fig_2.suptitle("Sector-wide production", fontsize=14, fontweight='bold')
        graph = fig_2.add_subplot(111)
        graph.plot(range(max_period), self.sector_wide_production_time_series["hash"], "b-")
        graph.plot(range(max_period), self.sector_wide_production_time_series["bean"], "g-")        
        max_values = [int(max(l)) for l in list(self.sector_wide_production_time_series.values())]
        graph.axis([0, max_period, 0, 1.2*max(max_values)])
        graph.set_ylabel("units")
        graph.set_xlabel("period")