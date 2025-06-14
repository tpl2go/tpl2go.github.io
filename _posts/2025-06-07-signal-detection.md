---
layout: post
title: Introduction to signal detection
layout: single
permalink: null
published: true
date: 2025-06-07
#category: stories
#tags: me
---
As someone working in a signal processing group, I have seen a fascinating diversity of signal detection methods used even within a small team. Signal detection is a ubiquitous, beginner-friendly problem, so it is no wonder a variety of algorithms exists for the multitudes of applications out there. While some algorithms employ heuristics, some others stand on theoretical grounding. 

Since I was recently tasked with teaching new engineers basic signal processing, I took the chance to consolidate my knowledge of signal detection. Hopefully this post can teach signal detection clearly and succinctly. 🤞

# Problem: Signal Detection
Lets start with the problem: Imagine that you have a burst of a complex-valued signal embedded in complex-valued gaussian noise that **varies** in power. How will you detect this burst?

![Signal in increasing noisefloor](/images/posts/signal-detection/baseproblem.png)

# Method 1: Static Threshold
Well, a fast and simple idea is to draw a static threshold. 

![Constant Energy Thresholding](/images/posts/signal-detection/sol1.png)

If the sample energy rises above threshold, we can count the sample as detected. But notice that some samples of the signal may still fall below the threshold. 

### Hysteresis Detection
To detect a contiguous segment, we can perform a hystersis detection. In other words, there are two static thresholds. The sample need to rise **above** the upper threshold to detect the **start the burst** and the sample need to fall **below** the lower threshold to detect the **end of the burst**. Hysteresis thresholding is sometimes called "edge detection".

![Hysteresis thresholding](/images/posts/signal-detection/sol1_hysteresis.png)

As can be seen in the figure above, the entire signal burst is detected as one segment. Due to the increasing noise floor, we also got some false alarms in the later part of the time series.

Hysteresis a viable method to detect radar signals as radar bursts often have constant power. But burst communications RF bursts may legitimately have instantaneous samples which dips to zero. This makes setting the lower threshold impossible. So instead, morphological operations can be used to directly clean up the breaks between the detections.

### Morphological Post-processing


Morphological operations work on binary arrays. For our application, we performed [binary closing](https://en.wikipedia.org/wiki/Closing_(morphology)) first to close up any breaks smaller than 5 samples long in the detected signal. Afterwards, we performed [binary opening](https://en.wikipedia.org/wiki/Opening_(morphology)) to remove any detected segments shorter than 5 samples long. 5 samples is just an heuristic choice of parameter. We can use other parameters for other applications.

![Morphological operation](/images/posts/signal-detection/sol1_morphological.png)

As can be seen in the figure above, there are fewer false alarms. We could have removed that false alarm had we performed binary opening with structure size greater than 5. 

# Method 2: Dynamic Threshold (CFAR)

As seen previously, static thresholding doesnt adapt to changing noise floor. Even if we have an environment where the noise floor is stationary, different receivers may have different gains can the scale of the received signal can vary widely, making it annoying to manually set static threshold. Can we set the threshold more dynamically?

Indeed we can set the threshold dynamically as a fixed multiplier of the noise floor level. In the example below, we have a moving estimate of the noise floor and threshold the signal against 5x of the noisefloor

![CFAR detection](/images/posts/signal-detection/sol2_cfar.png)

### Estimating noise floor
But how will we estimate the noise floor when signal is present?

In short, we can't. We have to use the parts of the time series without signal to estimate the noise floor. One way to create a moving estimate of the noise floor is to correlate a window as such the one below. 

![CFAR detection](/images/posts/signal-detection/CFAR_structure.png)

The middle sample is position whose noisefloor we are estimating. The "guard samples" are the samples we are ignoring as it may be the signal burst itself. The number of guard samples on each side should be at least as long as the burst length. The "reference samples" are the samples we use to esimate the noise floor. The more reference samples we use, the more precise our noise floor estimate, but inherently also assumes that if there are multiple bursts, they are spaced further apart.

![CFAR Operation](/images/posts/signal-detection/CFAR.gif)

<details>
<summary>Lazy alternative</summary>

Now, I am often lazy and it is a bit tedious to construct such a window in python to correlate. So I often simply use scipy's <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.median_filter.html">median_filter</a> to estimate the noisefloor and ensure that my window is at least 3x the size of the burst. I may sometimes divide the median filter's output by $log(2)$ to convert the median into a mean.
</details>
### Proving Constant False Alarm Rate
Now for some math to explain why this is sometimes called "constant false alarm rate" (CFAR).

In a complex random gaussian signal $x = a + ib$:
* $a \sim \mathcal{N}(0,\sigma^2)$
* $b \sim \mathcal{N}(0,\sigma^2)$

The energy of $x$ is $|x|^2 = a^2 + b^2$ where:
* $ \|x\| ^2  \sim Exponential(\lambda=\frac{1}{2\sigma^2}) $
* mean of $ \|x\| ^2 = 2\sigma^2$
* standard deviation of $ \|x\| ^2 = 2\sigma^2$

We sometimes also say that $ \|x\| ^2$ is chi-squared distributed with degree 2. This is also correct as a chi-squared distribution with $k=2$ is a scaled [exponential distribution](https://en.wikipedia.org/wiki/Exponential_distribution).

Now, assuming that we had set the threshold to be $m$ times the noise floor (mean of the noise distribution = $\frac{1}{\lambda}$ ).
* probability of false alarm = $exp(-\lambda (m\frac{1}{\lambda})) = exp(-m)$

Notice that the probability of false alarm is independent of the noise power $\sigma$. Thus the namesake. You may notice that in the figure above there are 6 false alarm samples which crosses the threshold. This fits theory because expected $exp(-5) * 1000 \approx 7$ false alarm samples. Elegant right? 😊

# Method 3: Matched Filter + CFAR
Can we do even better in our detection?

Well, if we know the signal that we are searching for then yes! Radars often know the exact burst that they transmitted. Communications bursts often have a known preamble at the start. By explicitly hunting for this known sequence through cross correlation, we can do better than relying on energy detection.

$$
y[t] = \sum_i s^*[i]x[t+i]
$$

![Cross Correlation](/images/posts/signal-detection/CrossCorrelation.gif)


The process of cross-correlating a known signal is often called "matched filtering" or "pulse compression" in radar. I find the term "Pulse Compression" an especially cute analogy because it intuitively describes the summation operation as "compressing" the burst into a single sample $y[t]$.

The element-wise multiplication of conjugate of the signal $s^*[i]$ serves to align the phase of every sample in the signal so that the summation is phase coherent. Because our signal was "compressed" in a phase coherent manner and the noise was "compressed" incoherently, the signal to noise ratio improves after matched filtering. If our signal is long, matched filtering allows the detection of very weak signal due to a significant integration gain.

![CFAR detection](/images/posts/signal-detection/sol3.png)

While previously we had to detect the "start of burst" and "end of burst", now we only have to detect a peak as the entire signal burst has been "compressed" into a single sample $y[t]$.

Matched Filtering doesnt address the issue of varying noise floor. If the noise floor is higher, the matched filtering output is also higher. So an adaptive threshold like CFAR is still needed after matched filtering.

Notice also that around the peak there is a "skirting". This skirting is due to our correlation window entering and exiting the signal region. So even though we have "compressed" the burst into a single peak, the CFAR guard samples still needs to be as long as the burst length itself.

# Method 4: Cosine Similarity

CFAR method estimates the noise floor from adjacent samples. But this assumes that there is no signal in those adjacent samples. This assumption may not always hold true. Is there a way to detect our burst or preamble without relying on adjacent samples?

Well, yes if we "normalize" our cross correlation. 

$$
q[t] = \frac{\langle x_t,s \rangle}{\Vert x_t \Vert \Vert s \Vert} = \frac{\sum_i s^*[i]x[t+i]}{\Vert x_t \Vert \Vert s \Vert}\\
$$


* $\langle \cdot, \cdot \rangle$ is a inner product between two vectors.
* $\Vert \cdot \Vert$ is the L2 norm of the vector.
* $x_t$ is a segment of the received signal of the same length as the template $s$ and starting at index $t$

![Cosine Similarity](/images/posts/signal-detection/sol4.png)

While the cosine similarity output $q$ is complex, its magnitude is between 0 and 1. The elegance of using cosine similarity for detection is that the threshold is easy to set. Not only can we set a static threshold despite varying noisefloor or signal power, the threshold is theoretically grounded. 

Specifically, the cosine similarity threshold is directly related to the Signal to Noise Ratio (SNR). 

$$
|q|^2 = \frac{SNR}{1+SNR}
$$

If we set a specific threshold $q'$, we know that implicity we would not be able to detect signal below SNR $=\frac{q'}{1-q'}$.

We also preserve the constant false alarm rate property as the distribution of the cosine similarity "noise floor" is a [generalized F-distribution](https://en.wikipedia.org/wiki/F-distribution), calculating the exact false alarm rate given a threshold is not as trivial as in the matched filter case, but following the same train of thought we can intuitively see that it would be constant (independent of noise power).