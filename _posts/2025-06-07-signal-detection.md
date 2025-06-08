---
layout: post
title: Intro to Signal Detection
layout: single
permalink: null
published: false
date: 2025-06-07
#category: stories
#tags: me
---


Imagine that you have a burst of signal embedded in noise that varies in power. How will you detect this burst?

![Signal in increasing noisefloor](/images/posts/signal-detection/baseproblem.png)

<details>

<summary>Code to generate burst within noise</summary>

{% highlight python %}

import numpy as np
np.random.seed(42)
import matplotlib.pyplot as plt

N = 1000  # total samples
m = 60  # burst size
snr = 10

# generate signal 
s = np.sqrt(snr) * np.exp(2j*np.pi*np.random.rand(m))

# generate noise
x = np.random.randn(N) + 1j*np.random.randn(N) 
x = x / np.std(x)
noisemultiplier = np.linspace(1,2.5,N)
x = x * noisemultiplier

# embed signal in noise
offset = 277
x[offset:(offset + m)] += s

# plot
fig = plt.figure()
plt.plot(np.abs(x))
plt.show()

{% endhighlight %}

</details>

# Method 1: Static Threshold


# Method 2: Dynamic Threshold (CFAR)


# Method 3: Matched Filter + CFAR


# Method 4: Cosine Similarity