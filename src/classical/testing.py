import numpy as np 
pi = np.pi 
for y in range(15): # N - 1, N = 2^n, n = num qubits 
    coeff = np.exp(-1j*1*pi/8 * y) + \
            np.exp(-1j*5*pi/8 * y) + \
            np.exp(-1j*9*pi/8 * y) + \
            np.exp(-1j*13*pi/8 * y) 
    if abs(coeff) < 1e-10: coeff=0
    print(y,coeff)