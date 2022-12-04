import itertools 
import random 
from base import Base

class SemiPrimeGenerator(Base):
    def __init__(self, name: str = 'SemiPrimeGenerator', verbose: bool = False):
        super().__init__(name, verbose)

    """ Class for generating list of semiprimes that can be used for testing 
    factoring algorithms in this project """
    def get_primes_sieve(self, upper_bound: int = 1000):
        """ Return a list of all primes up to upper_bound - 1.
        Reference: https://github.com/qiskit-community/qiskit-community-tutorials/blob/master/algorithms/shor_algorithm.ipynb
        """
        return list(itertools.takewhile(lambda p: p < upper_bound, self.sieve()))

    def get_n_semiprimes(self, num_semiprimes: int = 20, upper_bound: int = 1000):
        primes = self.get_primes_sieve(upper_bound=upper_bound)
        l = len(primes)
        semiprimes = [self.get_semiprime(upper_bound=upper_bound) \
            for _ in range(num_semiprimes)]
        return semiprimes

    def get_semiprime(self, upper_bound: int = 1000):
        """ Return a semiprime that is a product of exactly two prime numbers 
        p and q where 2 <= p,q < upper_bound.
        Reference: https://github.com/qiskit-community/qiskit-community-tutorials/blob/master/algorithms/shor_algorithm.ipynb
        """
        primes = self.get_primes_sieve(upper_bound=upper_bound)
        l = len(primes)
        # choose two random primes and return their product (a semiprime)
        p = primes[random.randrange(l)]
        q = primes[random.randrange(l)]
        return p*q
     
    def sieve(self):
        """ Sieve of Eratosthenes algorithm 
        Reference: https://github.com/qiskit-community/qiskit-community-tutorials/blob/master/algorithms/shor_algorithm.ipynb
        """
        d = {}
        yield 2
        for q in itertools.islice(itertools.count(3), 0, None, 2):
            p = d.pop(q, None)
            if p is None:
                d[q*q] = q
                yield q
            else:
                x = p + q
                while x in d or not (x&1):
                    x += p
                d[x] = p
