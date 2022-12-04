""" Module for factoring semiprime integers using classical / non-quantum / brute force approach. 
"""
import time 
from math import sqrt,gcd
from base import Base
import numpy as np 
from random import randint 

class ClassicalPrimeFactorization(Base):
    def __init__(self, name: str = 'ClassicalSolver', verbose: bool = False):
        super().__init__(name, verbose)

    # def factor(self, N):
    #     """ Calculate prime factors of N """
    #     start = time.time() 
    #     p, q = None, None
    #     for i in range(2, int(sqrt(N)) + 1):
    #         if N % i == 0:
    #             p = i 
    #             q = N // p 
    #             end = time.time()
    #             elapsed = round(end - start, 6)
    #             return {'N': N, 'factors': {'p': p, 'q': q}, 'elapsed_seconds': elapsed}
     
    def factor(self, N: int = None):
        """ Classically run shor's algorithm """
        factors_found = False 
        start = time.time()
        if N % 2 == 0: # first simply check if even. 
            end = time.time() 
            elapsed = round(end - start, 6)
            factors = {
                    'p': 2, 'q': N // 2
                }
            factors_found = True 

        attempts = 0
        while not factors_found:
            # Continue until solved. 
            attempts += 1
            # Get an initial guess g that is coprime to N (gcd is 1)
            g = randint(3, N-1)
            while gcd(g, N) != 1:
                g = randint(3, N-1)
            self.info(f'attempt={attempts}, g={g}')
            # Find period r of g^r mod N 
            # (i.e., r is smallest number such that g^r = 1 (mod N))
            z = list(range(N))
            y = [g ** z0 % N for z0 in z]
            r = z[y[1:].index(1)+1] 
            self.info(f'r={r}->r/2={r/2.}->g**(r/2.)={g**(r/2.)}')
            if r % 2 == 0: # continue. if odd, can't use r/2 exponent of g. 
                # x = g^[r/2] (mod N)
                x = (g ** (r / 2.)) % N
                if ((x + 1) % N) != 0: # continue. if = 0, guess another g. 
                    factors = {
                        'p': gcd(int(x)+1, N),
                        'q': gcd(int(x)-1, N)
                    }
                    end = time.time()
                    elapsed = round(end - start, 6)
                    factors_found = True
        return {
            'N': N, 
            'factors': factors, 
            'elapsed_seconds': elapsed
        }
         

            



        