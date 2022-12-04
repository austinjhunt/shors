from utils.semiprimes import SemiPrimeGenerator
from classical.solver import ClassicalPrimeFactorization
import matplotlib.pyplot as plt 
import numpy as np
import os 
from base import Base
from qskt.solver import QiskitShor

class Driver(Base):
    def __init__(self, name: str = 'Driver', verbose: bool = False):
        super().__init__(name, verbose)
        self.plots_dir = os.path.join(os.getcwd(), 'plots')
        os.makedirs(self.plots_dir, exist_ok=True)

    def plot_results(self, x: list = [], y: list = [], title: str = '', fname: str = ''):
        """ Plot provided results as line graph with N on X axis and time 
        required for factoring on Y (seconds)"""
        ax = plt.gca()
        ax.get_xaxis().get_major_formatter().set_useOffset(False)
        x,y = np.array(x), np.array(y)
        bestfit_x, bestfit_y = np.polyfit(x, y, 1)
        plt.scatter(x, y)
        plt.plot(x, bestfit_x * x + bestfit_y)
        plt.title(title)
        plt.xlabel('N (number to factor)')
        plt.ylabel('Time (seconds)')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, fname))

    def run_implementation(self, 
        solver: Base = None,
        semiprimes: list = [],
        plot_results: bool = True, 
    ):
        x = []
        y = []
        for i,sp in enumerate(semiprimes):
            result = solver.factor(sp)
            p,q,elapsed = result['factors']['p'], result['factors']['q'],result['elapsed_seconds']
            self.info(f'solver={solver.name}, i={i}, N={sp} => p={p},q={q}, sec={elapsed}')
            x.append(sp)
            y.append(elapsed)
        if plot_results:
            self.plot_results(
                x=x, 
                y=y,
                title=f'Time Required to Factor Semiprime into Primes (solver={solver.name})',
                fname=f'{solver.name.lower().replace(" ", "")}.png'
            )

    def run_classic_implementation(
        self, 
        semiprimes: list = [], 
        plot_results: bool = True
        ):
        """ Run classic factorization implementation """
        self.run_implementation(
            solver=ClassicalPrimeFactorization(verbose=self.verbose),
            semiprimes=semiprimes,
            plot_results=plot_results,
        )

    def run_qiskit_implementation(
        self, 
        semiprimes: list = [],  
        plot_results: bool = True):
        """ Run the Qiskit implementation of Shor's algorithm """
        self.run_implementation(
            solver=QiskitShor(verbose=self.verbose),
            semiprimes=semiprimes,
            plot_results=plot_results,
        )

if __name__ == "__main__":
    driver = Driver(verbose=True)
    semiprimes_generator = SemiPrimeGenerator()
    semiprimes = semiprimes_generator.get_n_semiprimes(
        num_semiprimes=20,
        upper_bound=25
    )
    
    # run classic implementation 
    driver.run_classic_implementation(
        semiprimes=semiprimes,
        plot_results=True
    )

    # # run qiskit implementation
    # driver.run_qiskit_implementation(
    #     semiprimes=[15],
    #     plot_results=True
    # )