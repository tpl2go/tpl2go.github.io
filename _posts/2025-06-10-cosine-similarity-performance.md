---
layout: post
title: Signal Detection - Performance of Cosine Similarity Signal Detector (4/4)
layout: single
permalink: null
published: true
date: 2025-06-10
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


In a previous post, we analysed the performance of matched filter as a signal detector. In this post we analyse another metric for signal detection, the cosine similarity. 

$$ 
q^2 = \frac{|\langle \underline{y}, \underline{x} \rangle|^2}{\Vert \underline{y} \Vert^2  \Vert \underline{x}  \Vert^2}
$$

Note:
* $ \| \cdot \| $ refers to absolute value of a complex-valued scalar
* $\Vert \cdot \Vert $ refers to the L2 norm of a complex valued vector

# Assumptions
To make statistical analysis of this hypothesis testing more tractable, let's assume that every element in vector $\underline{x}$ is unit modulus. This is a reasonable assumption for many radar and communications bursts.

Unlike our previous post, we shall also assume that the real part and imaginary part of every element in $\underline{\eta}$ is a standard normal gaussian with unit variance. We shall see why later.

# Distribution of $q^2$ when no signal present ($\mathcal{H}_0$ case)

## Numerator
First we analyse the numerator:

$$
\begin{aligned}
\text{Numerator of } q^2 &= |\langle \underline{y}, \underline{x} \rangle|^2 \\
&= \left| \sum_{i=1}^L (\underline{\eta}[i] * \underline{x}^*[i]) \right|^2 \\
&= \left| \sum_{i=1}^L \underline{\eta}'[i]  \right|^2 \\
&= \left| \eta'' \right|^2 \\
\end{aligned}
$$

Since $\underline{x}$ is unit modulus, element-wise multiplication with a random gaussian vector $\underline{\eta}$ is another random gaussian vector $\underline{\eta}'$. The sum of $L$ random complex gaussian elements of $\underline{\eta}'$ is itself a random complex gaussian scalar $\eta''$. $ \|\eta'' \|^2 $ is the sum of 2 squared gaussians (real and imaginary parts) each with variance $L$. So $ \| \eta'' \|^2$ is [scaled chi-squared distributed](https://en.wikipedia.org/wiki/Chi-squared_distribution) with degree of freedom $k=2$.

$$
\text{Numerator of } q^2 \sim L  \chi_2^2
$$

## Denominator
Now we analyse the denominator:

$$
\begin{aligned}
\text{Denominator of } q^2 &= \Vert \underline{y} \Vert^2  \Vert \underline{x}  \Vert^2\\
&= \left( \sum_{i=1}^L \left| \underline{\eta}[i] \right|^2 \right)  \left( \sum_{i=1}^L \left| \underline{x}[i] \right| ^2 \right) \\
&= L \left( \sum_{i=1}^L \left| \underline{\eta}[i] \right|^2 \right)
\end{aligned}
$$

Because every element of $\underline{\eta}$ is a standard complex random gaussian, $\Vert \eta \Vert$ is a sum $2L$ squared standard gaussians. So $\Vert \eta \Vert$ is [chi-squared distributed](https://en.wikipedia.org/wiki/Chi-squared_distribution) with degree of freedom $k=2L$.

$$
\text{Denominator of } q^2 \sim L \chi_{2L}^2
$$

## Results
Putting numerator and denominator together:

$$
q^2 \sim  \frac{L  \chi_2^2}{L \chi_{2L}^2} = \frac{\chi_2^2}{\chi_{2L}^2}
$$

$q^2$ is the ratio between two chi-squared distribution. While this looks like an F-distribution, it isn't as the numerator and denominator are not independent. Fortunately there is another distribution with a similar form:

$$
\begin{aligned}
\frac{X}{X+Y} &\sim Beta\left(\frac{k_1}{2},\frac{k_2}{2} \right)\\
\text{where}\\ 
X &\sim \chi^2_{k_1}\\
Y &\sim \chi^2_{k_2}\\
\end{aligned}
$$

Reformulating the numerator again:

$$
X = (N_{r1} + \dots + N_{rL})^2 + (N_{i1} + \dots + N_{iL})^2
$$

Reformulating the denominator again:

$$
\begin{aligned}
L \left[ N_{r1}^2 + \dots + N_{rL}^2 + N_{i1}^2 + \dots + N_{iL}^2 \right] 
&= X  + \underbrace{(L-1) \left[ N_{r1}^2 + \dots + N_{rL}^2 + N_{i1}^2 + \dots + N_{iL}^2 \right] - \text{crossterms}}_{\text{a } \chi^2 \text{ distribution with } df=2L-2?}

\end{aligned}
$$

Unfortunately I still could not work out the math but from empirical simulations, it seems that 

$$
q^2 \sim Beta(1,L-1)
$$

# Distribution of $q^2$ when signal is present ($\mathcal{H}_1$ case)

## Numerator 

First we analyse the numerator

$$
\begin{aligned}
\text{Numerator of } q^2 &= |\langle \underline{y}, \underline{x} \rangle|^2 \\
&= \left| \sum_{i=1}^L ((s\underline{x}[i] + \underline{\eta}[i]) \underline{x}^*[i]) \right|^2 \\
&= \left| \sum_{i=1}^L (s + \underline{\eta}'[i])  \right|^2 \\
&= \left| Ls + \eta'' \right|^2 \\
\end{aligned}
$$

$\eta''$ is a random gaussian with variance = $L$. So $q^2$ is [scaled non-central chi-squared distrbuted](https://en.wikipedia.org/wiki/Noncentral_chi-squared_distribution) with degree of freedom $k=2$ (real and imaginary parts) and noncentrality parameter $\lambda = Ls^2$ 

$$
q^2 \sim L \chi_{nc}^2(k=2, \lambda=Ls^2) 
$$

## Denominator 

Next we analyse the denominator

$$
\begin{aligned}
\text{Denominator of } q^2 &= \Vert \underline{y} \Vert^2  \Vert \underline{x}  \Vert^2\\
&= \left( \sum_{i=1}^L \left| sx[i]+\underline{\eta}[i] \right|^2 \right)  \left( \sum_{i=1}^L \left| \underline{x}[i] \right| ^2 \right) \\
&= L \left( \sum_{i=1}^L \left| s+\underline{\eta'}[i] \right|^2 \right)
\end{aligned}
$$

Recall that every element of $x$ is unit modulus. And since we are taking the L2 norm, we can fold the phase of $x[i]$ into $\eta$ to create a new random gaussian $\eta''$ with the same unit variance. So $\Vert y \Vert^2$ is [non-central chi-squared distrbuted](https://en.wikipedia.org/wiki/Noncentral_chi-squared_distribution) with degree of freedom $k=2L$ and noncentrality parameter $\lambda = s^2$ 

$$
q^2 \sim L \chi_{nc}^2(k=2L, \lambda=s^2) 
$$

## Results 

Putting numerator and denominator together, 

$$
q^2 \sim  \frac{L  \chi_{nc}^2(k=2, \lambda=Ls^2)}{L \chi_{nc}^2(k=2L, \lambda=s^2)}
$$

$q^2$ is the ratio between two non-central chi-squared distribution. Again, while this looks like a generalized F-distribution, it is not as the numerator and denominator are not independent. From empirical studies it seems that resultant distribution can be approximated by a beta distribution but I am still unable to work out the derivation of the $\alpha$ and $\beta$ parameters from $L$ and $\gamma$.

## Visualizing the distribution


![Distribution of cosine similarity q^2](/images/posts/signaldetection_perf_cosinesim/q2distribution_L_3.gif)
![Distribution of cosine similarity q^2](/images/posts/signaldetection_perf_cosinesim/q2distribution_L_10.gif)

## Receiver Operator Curves


![ROC of cosine similarity detector](/images/posts/signaldetection_perf_cosinesim/cosinesim_roc_L_3.png)
![ROC of cosine similarity detector](/images/posts/signaldetection_perf_cosinesim/cosinesim_roc_L_10.png)
