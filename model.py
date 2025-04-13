#Simulation of a insurance risk model
import numpy as np
from scipy import stats
from scipy.special import erfcinv
import matplotlib.pyplot as plt
import heapq
class InsuranceRiskModel:
    def __init__(self, new_pol_rate, lost_pol_rate, starting_capital, starting_policy_holders, new_pol_fun, pol_time_fun, next_claim, limit_time, pol_pay):
        self.new_pol_rate = new_pol_rate
        self.lost_pol_rate = lost_pol_rate
        
        self.new_pol_function =new_pol_fun
        self.time_pol_in_firm_func = pol_time_fun
        self.claim_fun = next_claim
        # self.money_claimed = money_claimed
        
        #Reference vars
        self.limit_time = limit_time
        self.pol_pay = pol_pay
        self.starting_capital = starting_capital
        self.initial_n_pols = starting_policy_holders
        
        self.rng = np.random.default_rng()
        
        #Simulation vars
        self.time = 0
        self.capital = starting_capital
        self.n_pols = starting_policy_holders
        self.lost_pols = 0
        self.events_queue = [] #heap
        self.events = {'new_policyholder': self.new_policyholder,
                       'lost_policyholder': self.lose_policyholder,
                       'claim': self.next_claim}
        self.pol_list = []
        
        #Meter en la firma n_pols policyholders
        for i in range(self.n_pols):
            # Determino cuando dejaran de ser policyholders.
            t_e = self.time_pol_in_firm_func(self.lost_pol_rate)
            t_e = self.time + t_e
            # Y agrego los eventos para simularlos.
            if t_e < self.limit_time:
                heapq.heappush(self.events_queue, (t_e, 'lost_policyholder', i))
                self.pol_list.append(i)
        
    def initialize(self):
        self.time = 0
        self.capital = self.starting_capital
        self.n_pols = self.initial_n_pols
        self.lost_pols = 0
        self.events_queue = []
        self.events = {'new_policyholder': self.new_policyholder,
                       'lost_policyholder': self.lose_policyholder,
                       'claim': self.next_claim}
        self.pol_list = []
        
        #Meter en la firma n_pols policyholders
        for i in range(self.n_pols):
            # Determino cuando dejaran de ser policyholders.
            t_e = self.time_pol_in_firm_func(self.lost_pol_rate)
            t_e = self.time + t_e
            # Y agrego los eventos para simularlos.
            if t_e < self.limit_time:
                heapq.heappush(self.events_queue, (t_e, 'lost_policyholder', i))
                self.pol_list.append(i)
        

    
    def next_new_policyholder(self):
        if self.time >= self.limit_time:
            return None
        t_e = self.rng.poisson(self.new_pol_rate)
        t_e = self.time + t_e
        if t_e < self.limit_time:
            heapq.heappush(self.events_queue, (t_e, 'new_policyholder'))
    
    def new_policyholder(self):
        pol_id = self.n_pols
        self.n_pols += 1
        # Genero el tiempo de permanencia
        t_e = self.time_pol_in_firm_func(self.lost_pol_rate)
        t_e = self.time + t_e
        if t_e < self.limit_time:
            heapq.heappush(self.events_queue, (t_e, 'lost_policyholder', pol_id))
            self.pol_list.append(pol_id)
    
    def lose_policyholder(self, pol_id):
        self.n_pols -= 1
        self.pol_list.remove(pol_id)
        self.lost_pols += 1
        
    #Una reclamacion viene con una cantidad de dinero que distribuye F (asumo la F se pasa como argumento)
    def next_claim(self):
        t_e, money = next_claim(self.rng, self.claim_fun)
        t_e = self.time + t_e
        if t_e < self.limit_time:
            heapq.heappush(self.events_queue, (t_e, 'claim', money))
        
    def run(self):
        self.next_new_policyholder()
        self.next_claim()
        while self.time <= self.limit_time:
            if not self.events_queue:
                continue
            event_tuple = heapq.heappop(self.events_queue)
            event_time = event_tuple[0]
            self.capital = self.capital + self.n_pols * self.pol_pay * (event_time - self.time)
            self.time = event_time
            event_type = event_tuple[1]
            if event_type == 'new_policyholder':
                self.events[event_type]()
            elif event_type == 'lost_policyholder':
                self.events[event_type](event_tuple[2])
            elif event_type == 'claim':
                self.capital -= event_tuple[2]
                self.events[event_type]()
    
# def new_client(rate):
#     return np.random.poisson(rate)

def policyholder_time_in_the_firm(rate):
    return np.random.exponential(1/rate)

def next_claim(rate, money_fun=None):
    """Devuelve el tiempo en el que se producira una reclamacion junto con el dinero que se reclamara."""
    if money_fun is None:
        return (np.random.poisson(rate), np.random.exponential(1))
    return (np.random.poisson(rate), money_fun())
