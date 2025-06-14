import numpy as np
np.random.seed(42)
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter, uniform_filter1d
from scipy.ndimage import binary_closing, binary_opening

N = 1000
m = 60

snrdb = 13
snr = 10**(snrdb/10)

s = np.sqrt(snr) * np.exp(2j*np.pi*np.random.rand(m))
x = np.random.randn(N) + 1j*np.random.randn(N) 
print(np.std(x))
x = x / np.std(x)
noisemultiplier = np.linspace(1,2.5,N)
x = x * noisemultiplier
offset = 277
x[offset:(offset + m)] += s
t = np.arange(N)
absx = np.square(np.abs(x))

fig = plt.figure(figsize=(9,3))
plt.plot(t[:offset], absx[:offset], color="C0")
plt.plot(t[offset-1:offset+m+1], absx[offset-1:offset+m+1], color="C1")
plt.plot(t[offset+m:], absx[offset+m:], color="C0")
plt.xlabel("sample index")
plt.ylabel("energy value of signal")
plt.tight_layout()
plt.savefig("baseproblem.png")
plt.show()

# Method 1: Energy Thresholding
fig = plt.figure(figsize=(9,3))
plt.plot(absx)
plt.axhline(16, color="r")
plt.title("Constant Energy Thresholding")
plt.xlabel("sample index")
plt.ylabel("energy value of signal")
plt.tight_layout()

for i, isi in enumerate(absx>16):
    if isi:
        plt.axvspan(i, i+1, color="C3", alpha=0.3)
plt.savefig("sol1.png")
plt.show()

def hysteresis_thresholding(xx, threshold1, threshold2):
    y = np.zeros_like(xx, dtype=bool)
    out = []
    prev_start: int = None
    for i, x in enumerate(xx):
        if prev_start is not None:
            if x < threshold1:
                out.append((prev_start, i-1))
                prev_start = None
        else:
            if x > threshold2:
                prev_start = i

        if prev_start is not None:
            y[i] = True
    return y, out

absx_mask, detected_segments = hysteresis_thresholding(absx, 4,16)

fig = plt.figure(figsize=(9,3))
plt.plot(absx)
plt.axhline(16, color="r")
plt.axhline(4, color="r")
plt.title("Hysteresis Thresholding")
plt.xlabel("sample index")
plt.ylabel("energy of signal")
for i1,i2 in detected_segments:
    plt.axvspan(i1, i2, color="C3", alpha=0.3)
plt.tight_layout()
plt.savefig("sol1_hysteresis.png")
plt.show()


absx_mask = binary_closing(absx_mask, np.ones(5))
absx_mask = binary_opening(absx_mask, np.ones(5))

fig = plt.figure(figsize=(9,3))
plt.plot(absx)
plt.title("Mophological Ops to clean up detections")
plt.xlabel("sample index")
plt.ylabel("energy value of signal")
plt.axhline(16, color="r")
absx_mask, detected_segments = hysteresis_thresholding(absx_mask, 0.5,0.5)
for i1,i2 in detected_segments:
    plt.axvspan(i1, i2, color="C3", alpha=0.3)
plt.tight_layout()
plt.savefig("sol1_morphological.png")
plt.show()

# Method 2: CFAR
noisefloor = median_filter(absx, size=4*m)/np.log(2)

fig = plt.figure(figsize=(10,3))
plt.plot(absx)
plt.plot(noisefloor, label="noisefloor", color='k')
# plt.plot(2* noisefloor, color="r", ls="--", label="threshold")
plt.legend()
plt.xlabel("sample index")
plt.ylabel("energy value of signal")
plt.tight_layout()
plt.savefig("sol2_nf.png")
# plt.title("CFAR")
plt.show()

cfar_multiplier = 5
cfar_threshold = cfar_multiplier * noisefloor
absx_nf_mask = absx > cfar_threshold
absx_nf_mask = binary_closing(absx_nf_mask, np.ones(5))
absx_nf_mask = binary_opening(absx_nf_mask, np.ones(5))
absx_nf_mask, detected_nf_segments = hysteresis_thresholding(absx_nf_mask, 0.5,0.5)

fig = plt.figure(figsize=(9,3))
plt.plot(absx)
plt.plot(noisefloor, label="noisefloor", color='k')
plt.plot(cfar_threshold, color="r", ls="--", label="threshold")
for i1,i2 in detected_nf_segments:
    plt.axvspan(i1, i2, color="C3", alpha=0.3)
plt.legend()
plt.title("CFAR")
plt.xlabel("sample index")
plt.ylabel("energy value of signal")
plt.tight_layout()
plt.savefig("sol2_cfar.png")
plt.show()

# Method 3: Matched filter CFAR

def matchfilter(x,s):
    nout = len(x) - len(s) + 1
    out = np.zeros(len(x), dtype=np.complex128)
    tmplt = s.conj() / np.linalg.norm(s)
    for i in range(nout):
        seg = x[i:i+len(s)]
        # seg = seg / np.linalg.norm(seg)
        out[i+m-1] = np.sum(seg * tmplt)

    return out

x_mf = matchfilter(x,s)

noisefloor_mf = median_filter(np.square(np.abs(x_mf)), size=4*m) / np.log(2)

fig = plt.figure(figsize=(9,3))
plt.plot(np.square(np.abs(x_mf)))
plt.plot(noisefloor_mf, label="noisefloor", color='k')
plt.plot(3* noisefloor_mf, color="r", ls="--", label="threshold")
plt.legend()
plt.title("matched filter + CFAR threshold")
plt.xlabel("sample index")
plt.ylabel("matched filtered output")
plt.tight_layout()
plt.savefig("sol3.png")
plt.show()



# Method 4: Cosine Similarity

def matchfilter_cs(x,s):
    nout = len(x) - len(s) + 1
    out = np.zeros(len(x), dtype=np.complex128)
    tmplt = s.conj() / np.linalg.norm(s)
    for i in range(nout):
        seg = x[i:i+len(s)]
        seg = seg / np.linalg.norm(seg)
        out[i+m-1] = np.sum(seg * tmplt)

    return out

qf = matchfilter_cs(x,s)


fig = plt.figure(figsize=(10,3))
plt.plot(np.abs(qf))
plt.axhline(0.6, color="r")
plt.title("cosine similarity")
plt.xlabel("sample index")
plt.ylabel("cosine similarity output")
plt.tight_layout()
plt.savefig("sol4.png")

plt.show()