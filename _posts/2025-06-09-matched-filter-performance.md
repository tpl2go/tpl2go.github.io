---
layout: post
title: Performance of Matched Filter Signal Detector
layout: single
permalink: null
published: true
date: 2025-06-09
#category: stories
#tags: me
---

How do you measure how good a signal detector is?

Fundamentally a signal detector is a sliding classifier. This classifier is classifying between two hypotheses:

$$
\begin{aligned}
\mathcal{H}_0 &: \underline{y} = \underline{\eta} \\
\mathcal{H}_1 &: \underline{y} = s\underline{x} + \underline{\eta}
\end{aligned}
$$

where $\underline{y}$ is our received signal vector, $\underline{x}$ is our expected signal vector, $\underline{\eta}$ is the gaussian noise vector and $s$ is a real valued scalar representing the strength of the signal.

Match Filter / Pulse Compression can be thought of as converting our received vector $\underline{y}$ into a test metric $q^2$ for hypothesis testing.

$$ 
q^2 = |\langle \underline{y}, \underline{x}^* \rangle|^2
$$

Lets assume that $\underline{x}$ is a constant modulus signal. This is common for many radar and communications bursts. The phase of each element in vector $\underline{x}$ can be random and independent because we assume that our received signal is at baseband. 

## Distribution of $q^2$ when no signal present ($\mathcal{H}_0$ case)

$$
\begin{aligned}
q^2 &= |\langle \underline{y}, \underline{x}^* \rangle|^2 \\
&= \left| \sum_{i=1}^L (\underline{\eta}[i] * \underline{x}^*[i]) \right|^2 \\
&= \left| \sum_{i=1}^L \underline{\eta}'[i]  \right|^2 \\
&= \Vert \underline{\eta}' \Vert^2 \\
&= \left| \eta'' \right|^2 \\
\end{aligned}
$$

Since $\underline{x}$ is unit modulus, element-wise multiplication with a random gaussian vector $\underline{\eta}$ is another random gaussian vector $\underline{\eta}'$. The sum of $L$ random complex gaussian elements of $\underline{\eta}'$ is itself a random complex gaussian scalar $\eta''$.

Without loss of generality, assume that the real and imaginary part of $\eta''$ are standard normals. So $q$ is [exponential distributed](https://en.wikipedia.org/wiki/Exponential_distribution) with inverse scale parameter $\lambda=1/2$. The energy of the noise vector $\underline{\eta}$ is 2.

$$
q^2 \sim Exp(\lambda=1/2)
$$

## Distribution of $q^2$ when signal is present ($\mathcal{H}_1$ case)


$$
\begin{aligned}
q^2 &= |\langle \underline{y}, \underline{x}^* \rangle|^2 \\
&= \left| \sum_{i=1}^L ((s\underline{x}[i] + \underline{\eta}[i]) * \underline{x}^*[i]) \right|^2 \\
&= \left| \sum_{i=1}^L (s + \underline{\eta}'[i])  \right|^2 \\
&= \left| Ls + \eta'' \right|^2 \\
\end{aligned}
$$

Because we already assumed the real and imaginary parts of $\eta''$ are standard normals, $q$ is [non-central chi-squared distrbuted](https://en.wikipedia.org/wiki/Noncentral_chi-squared_distribution) with degree of freedom $k= 2$ (real and imaginary parts) and noncentrality parameter $\lambda = L^2s^2$ 

$$
q^2 \sim \chi_{nc}^2(k=2, \lambda=L^2s^2) 
$$


## Visualizing the distribution

Now, in my theoretical setup of the signal detection problem, the parameters are burst length $L$ and signal amplitude $s$. The total noise energy across burst length is fixed at 2. So if $L$ varies, noise power in my theoretical setup changes. In practice we dont control the noise so it is more convenient to parameterize the problem through SNR $\gamma$ and burst length $L$. 

$$
SNR = \gamma = \frac{s^2}{2/L}
$$


Reparameterizing the equations in terms of SNR and burst length:

$$
\begin{aligned}
\mathcal{H}_0 &: q^2 \sim Exp(\lambda=1/2) \\
\mathcal{H}_1 &: q^2 \sim \chi_{nc}^2(k=2, \lambda=2L\gamma) \\
\end{aligned}
$$

![Distribution of matched filter q^2](/images/posts/compare_sig_detector/q2distribution.gif)

## Receiver Operator Curves
Recall CFAR?

It is a method of setting the decision threshold by some mulitplier of the noise distribution mean.
For a signal of fixed SNR, varying the CFAR threshold only tradeoff between the probability of detection and the probability of false alarm. The signal detector cannot improve both Pd and Pfa through tuning of CFAR thresholds. The overlap in the distributions of $q^2$ under the $\mathcal{H}_0$ and $\mathcal{H}_0$ cases defines how hard the classification problem is. If we want to improve the detector, we should find another test metric that we transform our received signal vector $\underline{y}$ into.

So this leads to the concept of measuring how good a detector is through the receiver operator curve.

![ROC of matched filter detector](/images/posts/compare_sig_detector/matchfilter_roc.png)
