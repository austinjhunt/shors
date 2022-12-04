# Implementing Shor's Algorithm with Qiskit, Q#, and cQASM

This project includes three implementations of [Shor's Algorithm](https://quantum-computing.ibm.com/composer/docs/iqx/guide/shors-algorithm), a widely popular and widely documented quantum algorithm for prime factorization of integers developed in 1994 by [Peter Shor](https://www.youtube.com/watch?v=6qD9XElTpCE&vl=en-US), an American professor of applied mathematics at MIT. One implementation uses [Qiskit](https://qiskit.org), another uses [cQASM from Quantum Inspire](https://www.quantum-inspire.com/kbase/cqasm/), and the last one uses [Q# from Microsoft](https://learn.microsoft.com/en-us/azure/quantum/overview-what-is-qsharp-and-qdk).

These implementations were researched and completed for a final project in **CS 8395 - Special Topics: Introduction to Quantum Computing** at [Vanderbilt University](https://vanderbilt.edu) taught by [Dr. Chuck Easttom](http://chuckeasttom.com/).

Below is an overview of the motivation for this project, the algorithm itself, as well as a high-level outline of the three implementations.

## Why implement Shor's algorithm?

Peter Shor is essentially a rockstar in the quantum computing world, so rather than diving into newer, more obscure quantum algorithms (which I was tempted to do) like the [Variational Quantum Eigensolver (VQE) algorithm](https://arxiv.org/abs/1304.3061) or the [Quantum Approximate Optimization Algorithm (QAOA)](https://arxiv.org/abs/1411.4028) for the CS 8395 final project &mdash; which are certainly interesting algorithms but offer less clear documentation &mdash; I wanted to come out of this Quantum Computing course with a strong understanding of one of the &mdash; if not _the_ &mdash; most popular quantum algorithms and a clear idea of **how** it threatens modern cryptography. More than that, prior to this project I had not worked with Microsoft's Q# or Quantum Inspire's cQASM, so this opened my eyes to the ins and outs of other quantum programming languages apart from the Qiskit SDK for Python with which I had prior experience.

## Overview of Shor's Algorithm

In short (rather, in _Shor_), Shor's Algorithm offers a method of efficiently factoring large psuedoprime integers into their prime factors using quantum computing. The implications of this algorithm are drastic considering the security of modern public key cryptography, or asymmetric cryptography, relies on the hardness of that factorization. Asymmetric cryptography (e.g., the RSA cryptosystem [published in 1977](https://dl.acm.org/doi/abs/10.1145/357980.358017)) is used all over the place, whether in digital signatures for verifying the integrity of transmitted messages, in SSL/TLS for protecting data integrity and confidentiality in transit, in authenticating members of a Windows domain network against Active Directory with Active Directory Certificate Services (AD CS), in banking, in telecommunications, in e-commerce, and more. If the prime factorization on which asymmetric cryptography relies for its security guarantees is cracked, there goes most of our online security. That's why Shor's Algorithm is worth studying.

### Number Theory

The approach taken to finding the prime factors of large integers in classical computing essentially just comes down to iteratively guessing factors and continuing as long as the guesses are wrong.

With Shor's algorithm, we're also guessing, but the approach is a bit different. Given a similar large integer _N_, we first guess some random integer _g_ that likely does not share any factors with _N_ (i.e., _g_ is **coprime** to _N_), and then we use quantum computing to essentially transform that bad guess _g_ into a new integer that probably _does_ share a factor with _N_. Note that this transformation of bad guesses into good guesses takes a very long time on a normal computer, but runs **very quickly on quantum computers**.

With Shor's algorithm, we aren't interested necessarily in directly guessing the factors of the large number _N_. Thanks to [Euclid's algorithm for finding common factors of two numbers](https://www.khanacademy.org/computing/computer-science/cryptography/modarithmetic/a/the-euclidean-algorithm), we can guess integers that simply share factors with N. If we used Euclid's algorithm to find a common factor _f1_ between a guessed integer _g_ and the large number _N_, then it's game over (in a good way), since you can just divide _N_ by that common factor _f1_ to get the _other factor_ _f2_; those two factors are all you need to break the encryption. However, it's _very_ unlikely that your randomly guessed number _g_ will actually share a factor with _N_ considering the *N*s used for modern encryption are massive numbers.

This is where that bad-guess-to-good-guess transformation comes into play. The transformation is based on a simple fact in mathematics. For any two **coprime** integers _a_ and _b_ that _do not share a factor_ (e.g. our bad guess _g_ and the large integer _N_), some power _p_ of _a_ will certainly produce some multiple _m_ of _b_ plus 1.

$$a^p = m * b + 1$$

So to put this into context with our (likely bad) guess _g_ and large number _N_, we can be certain that:

$$g^p = m * N + 1$$

for some integer _m_.

Now, the fun mathy part comes from subtracting the 1 from both sides to get

$$g^p - 1 = m * N$$

Factoring the left side a bit further gives us:

$$(g^{p/2} + 1)*(g^{p/2} - 1) = m * N$$

Those two factors on the left are exactly the "good" guesses that Shor's algorithm provides from the initial bad guess _g_. In short,
$$g \implies g^{p/2} \plusmn 1 = m * N$$
describes the transformation.

Now, since the right side is not just _N_, but _m_ * *N*, the two factors on the left (let's call them *a* and *b* from left to right) may be *multiples\* of factors of N rather than factors of N directly.

### 3 Problems

There are three problems with the equation
$$(g^{p/2} + 1)*(g^{p/2} - 1) = a * b = m * N$$

that necessitate the use of quantum computing for the implementation of this algorithm.

First, one of the guesses (_a_ or _b_) might itself be a factor of _N_. If that's the case, the other guess is a factor of _m_. If that is the case, neither guess is helpful.

Second, what if the power _p_ is odd? Then _p/2_ is not a whole number and our original guess _g_ raised to the power of _p/2_ is likely not whole either. We're working with integers exclusively with this factorization goal, so that's not good.

NOTE: based on experimental results, 37.5% percent of the time, a random guess _g_ transformed into $g \implies g^{p/2} \plusmn 1$ will **not** lead to an odd _p_ nor will it lead to _a_
or _b_ being a factor of _N_. Which means, 37.5% of the time, $g^{p/2} \plusmn 1$ will lead to a factor of N that breaks the decryption.

Third, we need to find _p_. That is, we need to know how many times to multiply our guess _g_ by itself to get a multiple _m_ of _N_ plus 1. This takes a ton of time on classical computers.

### The Algorithm

To find the power _p_ such that
$$ g^{p/2} \plusmn 1 = m * N$$
we need to set up a quantum computer that takes in an integer *x* as input, raises our initial bad guess *g* to the power of *x*, and keeps track of both *x* and the value of $g^x$. The computer should then use the value of $g^x$ and calculate how much bigger than a multiple (*m*) of $N$ it is, i.e.
$$r = (g^x) \text{ mod } (m * N) $$
where modulus arithmetic tells us that $r$ is just the remainder after dividing $g^x$ by $m*N$.
Remember that we want the remainder $r$ to be 1 (from the equation above $g^p = m * N + 1$).

Obviously the above approach can be handled with a classical computer assuming we're trying one value of the input _x_ at a time. However, with a quantum computer, we can provide a superposition of many values of _x_ as the input to the quantum algorithm, and the computation will run simultaneously on all of those values. This computation would result first in the superposition of all corresponding values of $g^x$ for each _x_ in the input superposition. Then, the next step should take _that_ superposition of all $g^x$ and compute the superposition of all corresponding _remainders_ $r$ where each $r_i$ is
$$r_i = (g^x)_i \text{ mod } (m * N) $$

With this, we can also leverage [quantum interference](https://qiskit.org/documentation/qc_intro.html?highlight=interference#interference) to get all of our "non-p" answers (i.e. results that are not the _p_ we are looking for) to destructively interfere with each other, i.e., to cancel each other out so we are only left with one possible answer: _p_.

### Period Finding

Here we introduce the concept of period finding, which is ultimately the problem that Shor's algorithm solves.
Assume you know $p$ such that
$$g^p = m*N + 1$$
where the 1 is the remainder $r$. Great. Now, assume you guess a random $p$, e.g. $p = 29$. Chances are, with that random guess, you'll get a value of $r$ that isn't equal to 1, e.g. $r=3$. So,
$$g^{29} = m * N + 3$$
What can we do with this? Well, if you take that same random guess 29, and instead raise $g$ to the power of that guess _plus_ $p$ (which is still unknown), you get the same remainder on the right:
$$g^{29 + p} = m * N + 3$$
In fact, if you add _any multiple of p_ to that random guess for _p_, you get the same remainder $r$:
$$g^{29 + [p, 2p, 3p, .... xp]} = m * N + 3$$

In short, that power $p$ that we are looking for to improve our initial bad guess $g$ has a "repeating" property such that if we take some power $x$ of $g$ and simply add or subtract some multiple of $p$ to that power (as above), the amount more than $m * N$ (i.e. the remainder $r$) stays the same.

Let's take a step back. Before, we looked at passing a superposition of all possible possible powers $p$ (we referred to them as $x$) into the quantum computer running Shor's algorithm. If we were to go ahead and measure the result from the remainder computation run on that superposition, that measurement would give us one possible value for the remainder, $r$, e.g. $r=3$.

With quantum computing, if the result measured (e.g. if $r=3$) could have been produced from multiple states within the input superposition of states (the superposition of $x$ values), then we can only be left with the superposition of just the states that could have resulted in that measurement. So if we measure the remainder computation output and get $r = 3$, then we're left with only all of the possible powers of $p$ that could have resulted in $r = 3$.

Combining that with the "repeating property" of $p$ discussed previously, each of those elements $x_i$ in the left-over superposition of possible powers of $p$ (that could have resulted in $r=3$) must be exactly $p$ apart from each other. Let's refer to that left-over superposition as $S$. Since a superposition can be represented as a wave function that shows probabilities of the individual states in that superposition, we can express this differently. The period of the wave function representing that leftover superposition must be $p$, which means the frequency of that wave function must be $\frac{1}{p}$. If you can find the frequency of that wave function, you can find $p$.

### Fourier Transforms

The Fourier Transform is by far the best tool for finding frequencies. There happens to be a **quantum-specific version** of the Fourier Transform that you can apply to the superposition $S$ (from before) which repeats with a frequency of $f = \frac{1}{p}$. When applied, this will cause all of the frequencies that are not actually present to destructively interfere with each other, and thus cancel each other out to leave only one possible frequency for the superposition $S$ having a value of $\frac{1}{p}$.

When you pass in a number $c$ to a Quantum Fourier Transform, you get back a superposition of other numbers, where each of those numbers is weighted such that when graphed they produce a wave function with a frequency of the number $c$. The higher the value of the input $c$, the higher the frequency of the output wave function (superposition).

In our case, we want to pass in a superposition of numbers $S$. When you pass a superposition of numbers to a Quantum Fourier Transform you get back a **superposition of superpositions**. Since, again, superpositions can be expressed as wave functions, we can then take each wave function within the superposition of wave functions and add them together which will produce one wave function that captures destructive interference between the individual wave functions as low values, or dips in the wave. Those dips represent the canceling out of low probability states in the input superposition.

Extending this idea to our specific context, if your input superposition $S$ consists of superpositions that are spread apart by some amount $p$ (our desired value), then the Fourier Transform will output one possible result of $\frac{1}{p}$ with everything else destructively interfering and canceling out as desired.

### Finally!

Once the frequency $f = \frac{1}{p}$ is obtained from the Quantum Fourier Transform of the superposition of superpositions $S$, we can find $p$ as easily as

$$\frac{1}{\frac{1}{p}} = p$$

And now, referring back to the 3 problems from before, as long as $p$ is even, and as long as
$$g^{\frac{p}{2}} \plusmn 1$$
is _not_ directly a multiple of $N$, then it shares factors with $N$. If that's the case, we can use Euclid's algorithm to _find_ those factors $a$ and $b$ which are ultimately the factors providing the security for public key infrastructure.


## Subproblems

As discussed in the [outline](../README.md#overview-of-shors-algorithm) of the theory underlying Shor's algorithm, we must address a few subproblems to implement the algorithm.

### Period Finding

First, we need to solve the **period finding problem**, i.e., we need to find the power $p$ such that our guess $g$ raised to the power $p$ gives a multiple $m$ of the large number $N$ plus 1, or

$$ g^p = m * N + 1$$

With the periodic function
$$f(x) = g^x \text{ mod } N$$
$g$ is less than $N$ and the two have no common factors (i.e. $g$ is a "bad guess" as described in the algorithm overview). The period $p$ is the smallest non-zero integer such that
$$g^p = m * N + 1 \implies g^p \text{ mod } N = 1$$

### [Quantum Phase Estimation](https://qiskit.org/textbook/ch-algorithms/quantum-phase-estimation.html)

First, since quantum phase estimation is defined on a unitary operator $\hat{U}$, let's define a unitary operator. As documented [here](http://vergil.chemistry.gatech.edu/notes/quantrev/node17.html), a unitary operator $\hat{U}$ is "some operator that preserves the **lengths** and **angles** between vectors and can be thought of as a type of rotation operator in abstract vector space." Or, in shorter mathematical terms, a unitary operator U is an operator whose inverse is equal to its adjoint: 

$$\hat{U}^{-1} = \hat{U}^{\dagger}$$
 
Matrix inversion is discussed in more detail [here](https://www.mathsisfun.com/algebra/matrix-inverse.html) and matrix adjoints (AKA conjugate transposes of matrices) are discussed in more detail [here](https://en.wikipedia.org/wiki/Conjugate_transpose).

As documented at the link above, **quantum phase estimation** is "one of the most important subroutines in quantum computing." Used by many different quantum algorithms (like Shor's), its objective is as follows: Given a unitary operator $U$ (previously denoted with $\hat{U}$) the algorithm estimates $\theta$ in $U| \psi\rangle = e^{2 \pi i \theta }| \psi\rangle$, where $| \psi \rangle$ is an eigenvector and $e^{2 \pi i \theta }$ is the corresponding eigenvalue of that eigenvector. In short, we're estimating eigenvalues of a unitary operator. Since $U$ is unitary, all of its eigenvalues have a norm (length) of 1.

So, Shor's solution to the **period finding problem** was to use quantum phase estimation on the unitary operator:
$$U| y \rangle = | gy \text{ mod } N \rangle$$

If we start with our register in the state $|1 \rangle$, each successive application of $U$ multiplies the current state of our register by $a \text{ (mod } N)$. After $r$ applications of that multiplication, the register arrives back at the original state $|1 \rangle$. For example, if our initial guess $g$ is 3 and $N$ is 35, and $p$ is the period we are trying to find:
$$U|1\rangle = | 3 \rangle$$
$$U^2|1\rangle = | 9 \rangle$$
$$U^3|1\rangle = | 27 \rangle$$
$$ ... $$
$$U^{(p - 1)}|1\rangle = | 12 \rangle$$
$$U^p|1\rangle = | 1 \rangle$$

The above cycle indicates that a superposition of states _in that cycle_ ($|u_o\rangle$) would be an eigenstate of $U$. Or, mathematically speaking,
$$|u_o\rangle = \frac{1}{\sqrt{p}} \sum_{k=0}^{p-1} | g^k \text{ mod } N$$
where p is the period of the superposition we're interested in finding.

Note that if we refer back to our definition of the quantum phase estimation equation, we are currently using an eigenvalue of 1 (i.e., $e^{2 \pi i \theta } = 1$) for this eigenstate (the superposition of states in the cycle), meaning the phase is the same for each basis state.

Let's generalize this to capture an eigenstate where the phase is _different_ for each basis state. Specifically, we can focus on the case where the phase of the $k$th state is proportional to $k$.

$$|u_1\rangle = \frac{1}{\sqrt{p}} \sum_{k=0}^{p-1} e^{-\frac{2 \pi i k}{p}} | g^k \text { mod } N$$

When expressed this way, the estimated eigenvalue

$$ U|u_1 \rangle = e^{\frac{2 \pi i }{p}}|u_1 \rangle$$
contains the period $p$ which we're looking for. The presence of $p$ in the quantum phase estimation ensures that the phase differences between the $p$ different basis states are equal. To further generalize, we can multiply the phase difference by some integer $s$:

$$|u_s\rangle = \frac{1}{\sqrt{p}} \sum_{k=0}^{p-1} e^{-\frac{2 \pi i s k}{p}} | g^k \text { mod } N$$
$$ U|u_s \rangle = e^{\frac{2 \pi i s }{p}}|u_s \rangle$$

This gives a unique eigenstate for each integer value of $s$ where $0 \leq s \leq p - 1$. Keeping in mind that $p$ is the period we're looking for such that our guess $g$ raised to $p$ gives a multiple $m$ of $N$ plus 1, or $g^p = m*N + 1$.

If we take the summation of those eigenstates, the different phases cancel out all computational basis states except $| 1\rangle$ as expressed below:
$$\frac{1}{\sqrt{p}}\sum_{s=0}^{p-1} |u_s \rangle = |1 \rangle$$

This is similar to the previously discussed step of getting the "left-over" superposition $S$ from the measurement of some single remainder value $r$, e.g., $r=3$, such that $S$ includes only the states that could have produced $r$ as the measurement result. That basis state $|1 \rangle$ is a superposition of eigenstates so doing quantum phase estimation on the unitary operator $U$ using the basis state $| 1 \rangle$ will measure a phase
$$\phi = \frac{s}{p}$$
where again, $s$ is some random integer between 0 and $p - 1$. This corresponds to the previously discussed step of obtaining the frequency of a superposition of superpositions $S$ via a Quantum Fourier Transform, which produces our $f = \frac{1}{p}$ such that we can easily find the period $p$. After this point, we can use the [continued fractions algorithm](https://en.wikipedia.org/wiki/Continued_fraction) on $\phi$ to find the period $p$.

### Quantum Fourier Transform (QFT)

We also need to apply the quantum fourier transform to our "superposition of superpositions" as described in the above section such that we can find a frequency ($\frac{1}{p}$) of our superposition obtained from measuring the initial remainder computation.


## Three Implementations

### Implementing Shor's Algorithm with [Qiskit](https://qiskit.org/) from [IBM Research](https://research.ibm.com/)

For the first implementation I chose to use [Qiskit](https://qiskit.org/), an open-source SDK developed by [IBM Research](https://research.ibm.com/) (and the Qiskit community) for working with quantum computers at the level of pulses, circuits, and application modules, all in the friendly and familiar [Python](https://python.org) language. Specifically, I used Python 3.10 for the developing and testing the implementation.
You can find the Qiskit implementation in the [qiskit](qiskit/README.md) directory.

### Implementing Shor's Algorithm with [cQASM from Quantum Inspire](https://www.quantum-inspire.com/kbase/cqasm/)

### Implementing Shor's Algorithm with [Q# from Microsoft](https://learn.microsoft.com/en-us/azure/quantum/overview-what-is-qsharp-and-qdk)

## Comparing Qiskit, Q#, & cQASM
### Speed 
### Expressiveness
### Comments
### Exception Handling
### Dependencies
### Prebuilt Module Availabilities
### Learning Curve 
