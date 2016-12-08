'''
Created on 07.12.2016
HashBeansEconomy/InputHandler.py
Copyright Johannes Katzer, 2016

This class implements both the numerical basis and the handing over of "distributed parameters" to the 
EconomyController.

To use it, there are two possibilities: 1) go to branch "integrate_InputHandler". 
2) Do the integration by yourself: an InputHandler object needs to be instantiated during the 
EconomyController.__init__ method: add "self.init_handler = InputHandler()" anywhere in the __init__ method.

The core peace of the InputHandler is getInitParams(self, agent_type, init_agent_data). It is used
to overwrite the content of some init_agent_data list in EconomyController.initializeAgents(). Then, instead 
of using the values defined in init_params.py, some parameters will be set to a random value according to 
some distribution. 

The InputHandler will only overwrite the value of a given initial parameter, if this parameter was 
flagged. Invoke InputHandler.setFlag(some_initial_parameter, "uniform") if you want the value of 
some_initial_parameter to be drawn uniformly. Set your flag(s) right after the instantiation of
InputHandler. After all flags are set call InputHandler.drawParams() to generate a list of random 
values for each flagged parameter.

All distributions depend on parameters, e.g. the uniform distribution needs a lower and an upper bar.
Those parameters are set to a default value saved in self.distribution_params. Change those params by
invoking InputHandler.indiDistrParams(param_name, distribution_name, distribution_specific_parameters).
E.g: "InputHandler.indiDistrParams('RELATIVE_PREFERENCE_HASH', 'beta', (3,4))" to set alpha = 3 and
beta = 4 in the beta-distribution of RELATIVE_PREFERENCE_HASH.
'''

from numpy import random as rng

from init_params import *

INITIAL_ECONOMY_DATA_STRINGS = ["TMAX", "NUMBER_OF_CONSUMERS", "NUMBER_OF_HASH_FIRMS", "NUMBER_OF_BEAN_FIRMS", "CAP_UNIT_PRICE_HASH", "CAP_UNIT_PRICE_BEAN"]
INITIAL_CONSUMER_DATA_STRINGS = ["SUBSISTENCE_NEED_HASH", "SUBSISTENCE_NEED_BEAN", "RELATIVE_PREFERENCE_HASH", "ENDOW"]
INITIAL_HASH_FIRM_DATA_STRINGS = ["INIT_MONEY_HASH", "INIT_CAP_HASH", "PER_CAP_COSTS_HASH", "FIX_COSTS_HASH", "QUADRATIC_COEFFICIENT_HASH", "LINEAR_COEFFICIENT_HASH", "MONEY_HOLDING_RATE_HASH", "DIVIDEND_RATE_HASH"]
INITIAL_BEAN_FIRM_DATA_STRINGS = ["INIT_MONEY_BEAN", "INIT_CAP_BEAN", "PER_CAP_COSTS_BEAN", "FIX_COSTS_BEAN", "QUADRATIC_COEFFICIENT_BEAN", "LINEAR_COEFFICIENT_BEAN", "MONEY_HOLDING_RATE_BEAN", "DIVIDEND_RATE_BEAN"]


class InputHandler():
    def __init__(self, no_of_consumers, no_of_hashfirms, no_of_beanfirms):  
        self.K_0 = no_of_consumers
        self.J_0 = no_of_hashfirms
        self.N_0 = no_of_beanfirms
        self.agents_to_numbers = {"Consumer": no_of_consumers, "HashFirm": no_of_hashfirms, "BeanFirm": no_of_beanfirms}
        self.enabled = True
        
        self.distribution_params = {}
        self.setDistributionParams()
        
        self.flagged_params = {}
        self.drawn_init_params = {}
    
    def getEnabledState(self):
        return self.enabled
        
    def switchEnabledState(self):
        self.enabled = not self.enabled
    
    def setFlag(self, initial_parameter, flag):
        """ init parameter is a string containing the name of some initial parameter in the language of init_params.py
        flag defines the distribution to be used in draws """
        self.flagged_params[initial_parameter] = flag

    def setDistributionParams(self):
        standard_uniform_params = (0,1)
        standard_beta_params = (1,2)
        self.distribution_params["SUBSISTENCE_NEED_BEAN"] = {"uniform": (2,8), "beta": standard_beta_params}
        self.distribution_params["RELATIVE_PREFERENCE_HASH"] = {"uniform": standard_uniform_params, "beta": standard_beta_params}
    
    def indiDistrParams(self, param_name, distribution_name, distribution_specific_parameters):
        self.distribution_params[param_name][distribution_name] = distribution_specific_parameters
        
    def drawParams(self):
        """ draws numbers to be used as values for some initial parameter
        does this for each flagged parameter
        and for each agent that needs that parameter """
        if self.flagged_params == {}: # empty dict -> no flags were set
            self.switchEnabledState() # => EconomyController.InputHandler will be set to None
        else:
            for param_name in self.flagged_params.keys():
                sample_size = self.agents_to_numbers[self.computeAgentType(param_name)]
                if param_name == "Endow":
                    pass # trickier than other init params, because Endow is a list not a float
                if self.flagged_params[param_name] == "uniform":
                    lower_bar, upper_bar = self.distribution_params[param_name]["uniform"]                    
                    self.drawn_init_params[param_name] = rng.uniform(lower_bar, upper_bar, sample_size)
                if self.flagged_params[param_name] == "beta":
                    alpha, beta = self.distribution_params[param_name]["beta"]
                    self.drawn_init_params[param_name] = rng.beta(alpha, beta, sample_size)
   
    def computeParamName(self, agent_type, idx):
        if agent_type == "Consumer":
            return INITIAL_CONSUMER_DATA_STRINGS[idx]
        elif agent_type == "HashFirm":
            return INITIAL_HASH_FIRM_DATA_STRINGS[idx]
        elif agent_type == "BeanFirm":
            return INITIAL_BEAN_FIRM_DATA_STRINGS[idx]
            
    def computeAgentType(self, param_name):
        if param_name in INITIAL_CONSUMER_DATA_STRINGS:
            return "Consumer"
        elif param_name in INITIAL_HASH_FIRM_DATA_STRINGS:
            return "HashFirm"    
        elif param_name in INITIAL_BEAN_FIRM_DATA_STRINGS:
            return "BeanFirm" 
            
    def getInitParamValue(self, param_name, pos): # numpy arrays don't implement .pop() method. That is the only reason for pos.
        return self.drawn_init_params[param_name][pos]  
        
    def getInitParams(self, agent_type, init_agent_data, pos):
        dupe = list(init_agent_data)
        for param in dupe:
            if isinstance(param, list): # Endow list is getting on my nerves...
                idx = 3
            else:
                idx = init_agent_data.index(param)
            param_name = self.computeParamName(agent_type, idx)
            try:
                flag = self.flagged_params[param_name]
            except KeyError: # parameter param was not flagged
                continue
            init_agent_data[idx] = self.getInitParamValue(param_name, pos)
        return init_agent_data
