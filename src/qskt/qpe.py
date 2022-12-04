""" Module for handling Quantum Phase Estimation. Shor's 
solution to the period finding problem was to use quantum 
phase estimation on the unitary operator:
$$U| y \rangle = | gy \text{ mod } N \rangle$$
"""
from qiskit import QuantumCircuit, Aer, transpile, assemble
from math import gcd 
import numpy as np
from base import Base 
from .qft import QuantumFourierTransform
class QuantumPhaseEstimator(Base):

    def __init__(self, name: str = 'QPE', verbose: bool = False):
        super().__init__(name, verbose)
        self.qft = QuantumFourierTransform()
        
    def a2jmodN(self, a: int = None, j: int = None, N: int = None):
        """Compute a^{2^j} (mod N) by repeated squaring. 
        This method is intended to provide some scalability to this algorithm 
        by removing the statically set N=15 requirement used in the docs.
        This is not currently used as I am not yet sure where to leverage it. 
        """
        for _ in range(j):
            a = np.mod(a**2, N)
        return a

    def quantum_phase_estimation_g_mod_n(self, g: int = None, N: int = None ):
        """ 
        Apply quantum phase estimation to estimate the phase for some "bad" integer guess g
        and some large number N whose factors need to be determined. 
        We want to find the period p such that g^p = m * N + 1, or g^p mod (m * N) = 1.
        """
        # Here we define the number of "counting qubits" such that we can 'count' on the
        # first n_count qubits of our circuit. 
        n_count = 8 

        # Create a quantum circuit; when defining the circuit, 
        # we add an extra 4 qubits for the unitary operator U
        # to act on. This will have n_count + 4 quantum registers and just
        # n_count classical registers. The classical registers are to 
        # allow the mapping of quantum measurement results to classical bits.
        circuit = QuantumCircuit(4 + n_count, n_count)

        # for those first n_count counting qubits, we want to initialize each one 
        # to a superposition state using an H (Hadamard) gate.
        # an H gate (Hadamard gate) transforms the qubit such that
        # the probability of measuring 0 from the qubit is equal to the 
        # probability of measuring 1 from the qubit
        # Very common initialization step in quantum programming.
        for q in range(n_count):
            circuit.h(q) 

        # apply single-qubit Pauli-X gate to the last qubit.
        # the Pauli-X gate is equivalent to a classical bit flip, i.e. where 0 becomes 1 and
        # 1 becomes 0.
        circuit.x(3+n_count) 

        # For each of the n_count "counting qubits", do controlled U operations 
        for qubit in range(n_count): 
            # for qubit i, append to the circuit a controlled U gate 
            # representing U^(2^i) repeated g mod N circuits (with each repetition multiplying on itself)
            # we ultimately want to obtain a phase s / p where g^p mod N = 1. 
            # This allows us to represent a superposition of all remainders r where 
            # each r_i = (guess ^ 2^i) mod N
            # We can then use that superposition of all remainders to find a period as discussed in the README.
            controlled_gate_instruction = self.c_amodN(g=g, p=2**qubit, N=N)
            # Append instruction to end of circuit, modifying in place.
            circuit.append(
                controlled_gate_instruction,
                [qubit] + [i + n_count for i in range(4)]
            )

        # We now have a superposition of all remainders r. 
        # We want to use the Quantum Fourier Transform to obtain a frequency from that superposition/wave function.
        # first, we need to append a QFTDagger gate (conjugate transpose of the QFT) to the circuit
        # to apply the inverse of the Quantum Fourier Transformation 
        # to the first n_count qubits of the circuit as defined above.
        circuit.append(self.qft.qft_dagger(n_count), range(n_count)) # Do inverse-QFT

        # We want to measure the results from the first n_count qubits, and 
        # map those results into corresponding n_count classical bits of our quantum circuit.
        circuit.measure(range(n_count), range(n_count))

        # We use the AER simulator to simulate results. 
        aer_sim = Aer.get_backend('aer_simulator')
        # Setting memory=True below allows us to see a list of each sequential reading
        t_circuit = transpile(circuit, aer_sim)
        qobj = assemble(t_circuit, shots=1)
        # Obtain the result from the simulation and print / display those results.
        result = aer_sim.run(qobj, memory=True).result()
        readings = result.get_memory()
        self.info("Register Reading: " + readings[0])

        # Cast the register reading to an integer and divide by 2 to the power of n_count
        # to get the phase, which corresponds to the frequency obtained from the QFT as discussed
        # in the README, where the frequency is 1/p, and p is the value we want. 
        phase = int(readings[0],2)/(2**n_count)
        self.info("Corresponding Phase: %f" % phase)
        return phase
        
    def c_amodN(self, g: int = None, p: int = None, N: int = None):
        
        """  
        To create U^p where U is a unitary operator, we repeat the circuit p times. 
        This is specifically written to achieve controlled multiplication by g mod N.
        Where: 
        g is some "bad" integer guess between 2 and 14 inclusive, 
        N is the number whose prime factors we want, and 
        p is such that g^p = m * N + 1 or g^p mod m*N = 1. 

        Tying this back into the README, if we consider our input superposition of all
        possible values of the power p, we are obtaining an output superposition of all 
        of the corresponding remainder values defined by r = g^p mod m*N, with N statically set as 15. 
        """
        if gcd(g, N) != 1:
            raise ValueError(f'g={g} and N={N} not coprime')

        # Create a circuit with 4 registers 
        # (a list of instructions bound to 4 registers)
        U = QuantumCircuit(4)

        ## Repeat the following execution p times to achieve U^p        
        for _ in range(p):   
            if g in [2,13]: 
                # use SWAP gate (equivalent to a state swap; classical logic gate)
                # to swap qubit 0 with qubit 1, qubit 1 with qubit 2, qubit 2 with qubit 3. 
                U.swap(0,1)
                U.swap(1,2)
                U.swap(2,3)
            if g in [7,8]:
                # use SWAP gate (equivalent to a state swap; classical logic gate)
                # to swap qubit 2 with qubit 3, qubit 1 with qubit 2, qubit 0 with qubit 1. 
                U.swap(2,3)
                U.swap(1,2)
                U.swap(0,1)
            if g in [4, 11]:
                # use SWAP gate (equivalent to a state swap; classical logic gate)
                # to swap qubit 1 with qubit 3, qubit 0 with qubit 2 
                U.swap(1,3)
                U.swap(0,2)
            if g in [7,11,13]:
                # apply Pauli-X gate on qubits 0, 1, 2, and 3
                # this gate essentially acts like a classical bit flip.
                # equivalent to a pi radian rotation about the X axis. 
                for q in range(4):
                    U.x(q)
        # Create one gate out of this whole repeated circuit.
        U = U.to_gate()
        # Name it after what it is specifically doing. 
        U.name = "%i^%i mod 15" % (g, p)
        # Return a controlled version of the gate U with default 1 contro added to gate. 
        c_U = U.control()
        return c_U