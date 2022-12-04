import numpy as np  
from math import gcd
import time 
from numpy.random import randint
from fractions import Fraction
import os 
import numpy as np 
from math import gcd
import os 
from .qpe import QuantumPhaseEstimator
from base import Base 
LOG_FOLDER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log')

class QiskitShor(Base):
    def __init__(self, name: str = 'QiskitShorSolver', verbose: bool = False):
        super().__init__(name, verbose)
        self.qpe = QuantumPhaseEstimator()
        self.name = name 
        self.verbose = verbose
        self.setup_logging()

    def _g_is_nontrivial_factor_of_n(self, g: int = None, n: int = None):
        return g not in [1,n] and (n % g) == 0

    def factor(self, N): 
        """ Run shors algorithm to leverage quantum computing 
        to find prime factors of large number N.
        Using shor's involves setting some requirements around the guessed values
        of N's factors. Specifically, they can't be trivial factors of N. 
        Also, the period p such that the guess ^ p mod m * N = 1 must be even.
        When these criteria are not met, the process must be restarted with a new initial 
        guess g. The reasoning behind these criteria is outlined in the README of this folder. 
        """
        attempts = 0
        factor_found = False 
        factors = None 
        start = time.time()
        if N % 2 == 0:
            attempts = 1
            factors = {'p': 2, 'q': N // 2}
            factor_found = True 
            end = time.time() 
            elapsed = round(end - start, 6)
        
        np.random.seed(1)
        while not factor_found:
            attempts += 1
            self.info(f'Attempt: {attempts}')
            g = randint(2, N)
            self.info(f'Guessed random initial number g={g} between 1 and N={N}')
            if gcd(g, N) != 1:
                self.info(f'gcd(g,N)=gcd({g},{N}) != 1. Retrying.')
                factors = {'p': g, 'q': N // g}
                factor_found = True 
                end = time.time() 
                elapsed = round(end - start, 6)
                break 
            # find a guess for the period p such that g^p mod m*N = 1 
            self.info(f'Getting phase phi = s / p from initial guess g = {g} in order to find period p')
            phase = self.qpe.quantum_phase_estimation_g_mod_n(
                g=g, 
                N=N
            ) # returns a phase phi = s / p such that we can find p 
            if phase != 0:
                self.info(f'Phase = {phase}. Denominator should tell us the period p. ')
                # The denominator should tell us the period (i.e. the frequency from 
                # the quantum fourier transform should tell us the period p of the superposition
                # obtained from measuring a result from the superposition of remainder values)
                # this is discussed in greater detail in the README.
                frac = Fraction(phase).limit_denominator(max_denominator=N) 
                s, p = frac.numerator, frac.denominator 
                self.info(f'The period p = {p}')
                self.info(f'g^p mod m * N = 1 => {g}^{p} mod m*{N} = 1, implies: ')
                self.info(f'(g^p - 1) mod N = ({g}^{p} - 1) mod {N} = 0')
                
                if p % 2 == 0: 
                    # if the period p is also even we can continue 
                    self.info(f'p = {p} is even, continuing...')
                    self.info(f'g^p - 1 = {g}^{p} - 1 = a * b = (g ^(p/2) - 1) * ((g ^ (p/2)) + 1) = ({g} ^({p}/2) - 1) * (({g} ^ ({p}/2)) + 1) ')
                    self.info(f'There is a high probability that the GCD of N={N} and either a=(g ^(p/2) - 1) or b=((g ^ (p/2)) + 1) is a proper factor of N')

                    guesses = [gcd(g**(p//2)-1, N), gcd(g**(p//2)+1, N)]
                    for guess in guesses:
                        if self._g_is_nontrivial_factor_of_n(g=guess, n=N):  
                            factors = {'p': guess, 'q': N // guess}
                            factor_found = True
                            end = time.time() 
                            elapsed = round(end - start, 6)
                            break 
                else: 
                    self.info(f'Period p = {p} is not even. Re-attempting factorization.')
            else: 
                self.info(f'phase returned from Quantum Phase Estimation is 0. Re-attempting factorization.')
        return {
            'attempts': attempts,
            'elapsed_seconds': elapsed,
            'factors': factors,
            'N': N
        }
      