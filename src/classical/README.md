# Classical Prime Factorization
In this directory I've created a small script ([main.py](main.py)) for demonstrating a classical, brute-force approach to factoring semiprime numbers into their prime factors (where a semiprime number is a number with exactly two prime factors, e.g. 25 = 5 * 5).

First, I obtain a list of $N$ semiprime numbers. To do this, I use the Sieve of Eratosthenes algorithm for generating a list of prime numbers below an *upper_bound*, e.g., $1000$, and then I build a list of $N$ different products of $p*q$, where $p$ and $q$ are each chosen randomly from the list of primes. Both $N$ and *upper_bound* are parameterized. 

After that, I sort the list of semiprimes from smallest to largest and simply iterate over that list, calling the `factor(sp)` method for each semiprime `sp`. 
An example response looks as follows (for `10` semiprimes within an upper bound of `10000`):
```
{'N': 14581, 'p': 7, 'q': 2083, 'elapsed_seconds': 6.9141387939453125e-06}
{'N': 1992869, 'p': 641, 'q': 3109, 'elapsed_seconds': 4.291534423828125e-05}
{'N': 2614603, 'p': 277, 'q': 9439, 'elapsed_seconds': 1.5735626220703125e-05}
{'N': 4522897, 'p': 1787, 'q': 2531, 'elapsed_seconds': 0.0002880096435546875}
{'N': 6811991, 'p': 2243, 'q': 3037, 'elapsed_seconds': 0.0001690387725830078}
{'N': 8743201, 'p': 2287, 'q': 3823, 'elapsed_seconds': 0.00022602081298828125}
{'N': 17157809, 'p': 1783, 'q': 9623, 'elapsed_seconds': 0.00022411346435546875}
{'N': 17385481, 'p': 2417, 'q': 7193, 'elapsed_seconds': 0.0001971721649169922}
{'N': 21230701, 'p': 2143, 'q': 9907, 'elapsed_seconds': 0.001725912094116211}
{'N': 44733193, 'p': 5153, 'q': 8681, 'elapsed_seconds': 0.0038840770721435547}
```
N is the number being factored, p and q are the prime factors of N, and elapsed seconds is the time taken to find the factors. 