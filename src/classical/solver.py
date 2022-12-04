""" Module for factoring semiprime integers using classical / non-quantum / brute force approach. 
"""
import time 
from math import sqrt
from base import Base

class ClassicalPrimeFactorization(Base):
    def __init__(self, name: str = 'ClassicalSolver', verbose: bool = False):
        super().__init__(name, verbose)

    def factor(self, N):
        """ Calculate prime factors of N """
        start = time.time() 
        p, q = None, None
        for i in range(2, int(sqrt(N)) + 1):
            if N % i == 0:
                p = i 
                q = N // p 
                end = time.time()
                elapsed = round(end - start, 6)
                return {'N': N, 'factors': {'p': p, 'q': q}, 'elapsed_seconds': elapsed}
     