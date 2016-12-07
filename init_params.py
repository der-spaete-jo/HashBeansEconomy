'''
Created on 05.12.2016
HashBeansEconomy/init_params.py
Copyright Johannes Katzer, 2016
'''

from random import randrange

""" Program organization """
RANDOM_SEED = '129D5F'			# not implemented yet (run the model two times with same randomness for comparability)

""" Initial economy data """
TMAX = 20                      #how many rounds?
NUMBER_OF_CONSUMERS = 50        # K_0
NUMBER_OF_HASH_FIRMS = 15       # J_0
NUMBER_OF_BEAN_FIRMS = 15       # N_0
CAP_UNIT_PRICE_HASH = 2        # p_H
CAP_UNIT_PRICE_BEAN = 2        # p_B

""" Initial consumer data """
SUBSISTENCE_NEED_HASH = 4       # h_sn
SUBSISTENCE_NEED_BEAN = 6       # b_sn
RELATIVE_PREFERENCE_HASH = 0.5  # a
ENDOW = []                      # [Endow_0,...,Endow_TMAX]
Endow_0 = 20
ENDOW.append(Endow_0)
for T in range(TMAX):
    Endow_T = randrange(18,23)
    ENDOW.append(Endow_T)

""" Initial hash firm data """
INIT_MONEY_HASH = 25                # Money_0
INIT_CAP_HASH = 30                  # Cap_0
PER_CAP_COSTS_HASH = 0.07           # f
FIX_COSTS_HASH = 0.25               # F
QUADRATIC_COEFFICIENT_HASH = 0.015   # S
LINEAR_COEFFICIENT_HASH = 0.3       # R
MONEY_HOLDING_RATE_HASH = 0.8       # m
DIVIDEND_RATE_HASH = 0.02           # d

""" Initial bean firm data """
INIT_MONEY_BEAN = 25                # Money_0
INIT_CAP_BEAN = 30                  # Cap_0
PER_CAP_COSTS_BEAN = 0.07           # f
FIX_COSTS_BEAN = 0.25               # F
QUADRATIC_COEFFICIENT_BEAN = 0.015   # S
LINEAR_COEFFICIENT_BEAN = 0.3       # R
MONEY_HOLDING_RATE_BEAN = 0.8       # m
DIVIDEND_RATE_BEAN = 0.02           # d

