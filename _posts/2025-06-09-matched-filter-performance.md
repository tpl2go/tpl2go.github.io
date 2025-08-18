---
layout: post
title: Signal Detection : Performance of Matched Filter Detector (3/4)
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

where $\underline{y}$ is our complex-valued received signal vector, $\underline{x}$ is our complex-valued signal vector, $\underline{\eta}$ is the complex gaussian noise vector and $s$ is a real valued scalar representing the strength of the signal.

Match Filter / Pulse Compression can be thought of as converting our received vector $\underline{y}$ into a test metric $q^2$ for hypothesis testing.

$$ 
q^2 = |\langle \underline{y}, \underline{x} \rangle|^2
$$

## Assumptions
To make statistical analysis of this hypothesis testing more tractable, let's assume that every element in vector $\underline{x}$ is unit modulus. This is a reasonable assumption for many radar and communications bursts.

Additionally, assume that $\Vert \underline{\eta} \Vert^2 = 2$. We shall see why later. Every element in $\underline{\eta}$ is also an independent zero-mean complex random gaussian with equal variance in its real and imaginary parts.

Note:
* $ \| \cdot \| $ refers to absolute value of a complex-valued scalar
* $\Vert \cdot \Vert $ refers to the L2 norm of a complex valued vector

## Distribution of $q^2$ when no signal present ($\mathcal{H}_0$ case)

$$
\begin{aligned}
q^2 &= |\langle \underline{y}, \underline{x} \rangle|^2 \\
&= \left| \sum_{i=1}^L (\underline{\eta}[i] * \underline{x}^*[i]) \right|^2 \\
&= \left| \sum_{i=1}^L \underline{\eta}'[i]  \right|^2 \\
&= \left| \eta'' \right|^2 \\
\end{aligned}
$$

Since $\underline{x}$ is unit modulus, element-wise multiplication with a random gaussian vector $\underline{\eta}$ is another random gaussian vector $\underline{\eta}'$. The sum of $L$ random complex gaussian elements of $\underline{\eta}'$ is itself a random complex gaussian scalar $\eta''$.

We had assumed that $\Vert \underline{\eta} \Vert^2 = 2$ so that the real and imaginary part of $\eta''$ are standard normals with unit variance. This way, we can easily understand $q^2$ from the definition of a [chi-squared distribution](https://en.wikipedia.org/wiki/Chi-squared_distribution). From wikipedia, a chi-squared distribution with 2 degrees of freedom is an [exponential distribution](https://en.wikipedia.org/wiki/Exponential_distribution) with inverse scale parameter $\lambda=1/2$. So

$$
q^2 \sim Exp(\lambda=1/2)
$$

## Distribution of $q^2$ when signal is present ($\mathcal{H}_1$ case)


$$
\begin{aligned}
q^2 &= |\langle \underline{y}, \underline{x} \rangle|^2 \\
&= \left| \sum_{i=1}^L ((s\underline{x}[i] + \underline{\eta}[i]) * \underline{x}^*[i]) \right|^2 \\
&= \left| \sum_{i=1}^L (s + \underline{\eta}'[i])  \right|^2 \\
&= \left| Ls + \eta'' \right|^2 \\
\end{aligned}
$$

Again because we already assumed the real and imaginary parts of $\eta''$ are standard normals, $q^2$ is [non-central chi-squared distrbuted](https://en.wikipedia.org/wiki/Noncentral_chi-squared_distribution) with degree of freedom $k= 2$ (real and imaginary parts) and noncentrality parameter $\lambda = L^2s^2$ 

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

![Distribution of matched filter q^2](/images/posts/signaldetection_perf_matchedfilter/q2distribution_L_3.gif)
![Distribution of matched filter q^2](/images/posts/signaldetection_perf_matchedfilter/q2distribution_L_10.gif)

## Receiver Operator Curves
Recall CFAR?

It is a method of setting the decision threshold by some mulitplier of the noise distribution mean.
For a signal of fixed SNR, varying the CFAR threshold only tradeoff between the probability of detection and the probability of false alarm. The signal detector cannot improve both Pd and Pfa through tuning of CFAR thresholds. The overlap in the distributions of $q^2$ under the $\mathcal{H}_0$ and $\mathcal{H}_0$ cases defines how hard the classification problem is. If we want to improve the detector, we should find another test metric that we transform our received signal vector $\underline{y}$ into.

So this leads to the concept of measuring how good a detector is through the receiver operator curve.

![ROC of matched filter detector](/images/posts/signaldetection_perf_matchedfilter/matchfilter_roc_L_3.png)
![ROC of matched filter detector](/images/posts/signaldetection_perf_matchedfilter/matchfilter_roc_L_10.png)
