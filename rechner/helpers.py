import numpy as np
from rechner import constants as C


def get_first_and_last(data):
    
    _, i_first_unique= np.unique(data[:,C.iC], return_index=True)
    i_last_unique = np.append(i_first_unique[1:]-1, [len(data[:,C.iC])-1])
        
    data[i_first_unique, iF] = 1
    data[i_last_unique, iF]  = 1
    
    return data
    
        
        
