
from qiskit import QuantumCircuit
from math import pi
from base import Base

class QuantumFourierTransform(Base):

    def __init__(self, name: str = 'QFT', verbose: bool = False):
        super().__init__(name, verbose=verbose)

    def qft_dagger(self, n):
        """Apply N-qubit QFTdagger to the first n qubits of a circuit.
        
        QFT dagger is the conjugate transpose of the Quantum Fourier Transform,
        where the quantum fourier transform is used to find a frequency of a 
        given superposition. 
        """ 
        # Defining a new quantum circuit of n qubits. 
        circuit = QuantumCircuit(n)

        # for each qubit in the first half of that circuit
        for qubit in range(n//2):
            # Apply a SWAP gate to swap:
            #  qubit 0 with the n - 1 qubit
            #  qubit 1 with the n - 2 qubit
            #  qubit 2 with the n - 3 qubit
            # ... such that you are inverting the first n qubits
            circuit.swap(qubit, n - qubit - 1)

        # for each qubit j in the full circuit
        for j in range(n):
            # for each qubit preceding j 
            for m in range(j): 
                # apply a Controlled-Phase gate
                # This is a diagonal and symmetric gate that induces a 
                # phase/rotation on the state of the target qubit, depending on the control state.
                # Define the rotation angle as (-pi) / 2^(j-m)
                rotation_angle = -pi/float(2**(j-m))
                # apply the controlled-phase gate to qubit j using that rotation angle, 
                # using m as the control qubit, and using j as the target qubit
                circuit.cp(rotation_angle, control_qubit=m, target_qubit=j)
            
            # Apply Hadamard gate to qubit j to 
            # put it into a superposition such that probability of 0 = probability of 1
            circuit.h(j)

        # Give the Quantum Fourier Transform Dagger (conjugate transpose) 
        # circuit a name and then return it 
        circuit.name = "QFT†"
        return circuit
    