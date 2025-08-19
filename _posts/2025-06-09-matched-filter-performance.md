---
layout: post
title: Signal Detection - Performance of Matched Filter Detector (3/4)
layout: single
permalink: null
published: true
date: 2025-06-09
#category: stories
#tags: me
---


In the [first post on signal detection]({% post_url 2025-06-07-signal-detection %}), we mentioned that if we know the signal we wish to detect, we can perform two types of cross correlation:
* Matched Filtering with CFAR thresholding
* Cosine Similarity with static thresholding

Which method should we use? Which method is better?

This note attempts to answer this question analytically and through simulations.

# Problem Formulation: Hypothesis Testing
We could formulate a cross correlation based signal detector as a sliding classifier. The classifier chooses between two possible hypotheses at every sample instance:

$$
\begin{aligned}
\mathcal{H}_0 &: \underline{y} = \underline{\eta} \\
\mathcal{H}_1 &: \underline{y} = s\underline{x} + \underline{\eta}
\end{aligned}
$$

where: 
* $\underline{y}$ is our complex-valued received signal vector
* $\underline{x}$ is our complex-valued signal vector
* $\underline{\eta}$ is the complex gaussian noise vector and 
* $s$ is a real valued scalar representing the strength of the signal.

The classifier maps the physical observable $\underline{y}$ into a real valued test statistic $z$ for decision making through thresholding 

Matched Filtering's test statistic : 
$$ z_{mf} = |\langle \underline{y}, \underline{x} \rangle|^2 $$

Cosine Similarity's test statistic: 
$$ z_{cs} = \frac{|\langle \underline{y}, \underline{x} \rangle|^2}{\Vert \underline{y} \Vert^2  \Vert \underline{x}  \Vert^2}$$

Where:
* $ \| \cdot \| $ refers to absolute value of a complex-valued scalar
* $\Vert \cdot \Vert $ refers to the L2 norm of a complex valued vector


## Assumptions
To make statistical analysis of this hypothesis testing more tractable, 
let's assume that every element in vector $\underline{x}$ is unit modulus. 
This is a reasonable assumption for many radar and communications bursts.

Additionally, assume that $\Vert \underline{\eta} \Vert^2 = 2$. We shall see why later. Every element in $\underline{\eta}$ is also an independent zero-mean complex random gaussian with equal variance in its real and imaginary parts.

Note:
* $ \| \cdot \| $ refers to absolute value of a complex-valued scalar
* $\Vert \cdot \Vert $ refers to the L2 norm of a complex valued vector

# Analysis of Match Filter test statistic

## Distribution of $z$ when no signal present ($\mathcal{H}_0$ case)

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

## Distribution of $z$ when signal is present ($\mathcal{H}_1$ case)


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


### Visualizing the distribution

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

### Receiver Operator Curves
Recall CFAR?

It is a method of setting the decision threshold by some mulitplier of the noise distribution mean.
For a signal of fixed SNR, varying the CFAR threshold only tradeoff between the probability of detection and the probability of false alarm.. 
The signal detector cannot improve both Pd and Pfa through tuning of CFAR thresholds. 
The overlap in the distributions of $q^2$ under the $\mathcal{H}_0$ and $\mathcal{H}_0$ cases defines how hard the classification problem is. 
If we want to improve the detector, we should find another test metric that we transform our received signal vector $\underline{y}$ into.

So this leads to the concept of measuring how good a detector is through the receiver operator curve.

![ROC of matched filter detector](/images/posts/signaldetection_perf_matchedfilter/matchfilter_roc_L_3.png)
![ROC of matched filter detector](/images/posts/signaldetection_perf_matchedfilter/matchfilter_roc_L_10.png)

# Analysis of cosine similarity test statistic
## Distribution of $q^2$ when no signal present ($\mathcal{H}_0$ case)

### Numerator
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

### Denominator
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

### Results
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

## Distribution of $z$ when signal is present ($\mathcal{H}_1$ case)

### Numerator 

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

### Denominator 

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

### Results 

Putting numerator and denominator together, 

$$
q^2 \sim  \frac{L  \chi_{nc}^2(k=2, \lambda=Ls^2)}{L \chi_{nc}^2(k=2L, \lambda=s^2)}
$$

$q^2$ is the ratio between two non-central chi-squared distribution. Again, while this looks like a generalized F-distribution, it is not as the numerator and denominator are not independent. From empirical studies it seems that resultant distribution can be approximated by a beta distribution but I am still unable to work out the derivation of the $\alpha$ and $\beta$ parameters from $L$ and $\gamma$.

### Visualizing the distribution


![Distribution of cosine similarity q^2](/images/posts/signaldetection_perf_cosinesim/q2distribution_L_3.gif)
![Distribution of cosine similarity q^2](/images/posts/signaldetection_perf_cosinesim/q2distribution_L_10.gif)

### Receiver Operator Curves


![ROC of cosine similarity detector](/images/posts/signaldetection_perf_cosinesim/cosinesim_roc_L_3.png)
![ROC of cosine similarity detector](/images/posts/signaldetection_perf_cosinesim/cosinesim_roc_L_10.png)