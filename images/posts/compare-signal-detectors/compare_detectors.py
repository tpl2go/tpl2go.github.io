import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics

def simulate(snr, L=1):
    N = 10**5
    sim_0 = np.random.randn(N, L) + 1j * np.random.randn(N, L)
    sig = np.ones_like(sim_0)
    sim_1 = np.sqrt(snr*2) * sig + sim_0
    mf_q2_0 = np.square(np.abs(np.sum(sim_0 * sig.conj(), axis=1)))
    mf_q2_1 = np.square(np.abs(np.sum(sim_1 * sig.conj(), axis=1)))

    signorm2 = np.square(np.linalg.norm(sig, axis=1))
    y0norm2 = np.square(np.linalg.norm(sim_0, axis=1))
    y1norm2 = np.square(np.linalg.norm(sim_1, axis=1))
    cs_q2_0 = np.square(np.abs(np.sum(sim_0 * sig.conj(), axis=1)))/y0norm2/signorm2
    cs_q2_1 = np.square(np.abs(np.sum(sim_1 * sig.conj(), axis=1)))/y1norm2/signorm2

    return cs_q2_0, cs_q2_1, mf_q2_0, mf_q2_1

def plot_roc(L = 3):

    fig, ax = plt.subplots()
    for i,snrdb in enumerate([-6,-3,0,3,6]):
        snr = 10**(snrdb/10)
        cs_q2_0, cs_q2_1, mf_q2_0, mf_q2_1 = simulate(snr, L)

        y_true = np.concatenate((np.zeros_like(cs_q2_0), np.ones_like(cs_q2_1)))
        scores = np.concatenate((cs_q2_0, cs_q2_1))
        cs_fpr, cs_tpr, thresholds = metrics.roc_curve(y_true, scores)

        y_true = np.concatenate((np.zeros_like(mf_q2_0), np.ones_like(mf_q2_1)))
        scores = np.concatenate((mf_q2_0, mf_q2_1))
        mf_fpr, mf_tpr, thresholds = metrics.roc_curve(y_true, scores)

        ax.plot(cs_fpr, cs_tpr, alpha=0.6, color=f'C{i}', label=f'Cosine Sim: {snrdb} dB')
        ax.plot(mf_fpr, mf_tpr, alpha=0.6, color=f'C{i}', linestyle='--', label=f'Match Filter: {snrdb} dB')

    ax.legend()
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title(f'ROC curves of two signal detectors (L={L})')
    plt.savefig(f'roc_L_{L}.png')
    plt.show()

plot_roc(L = 3)
plot_roc(L = 10)
plot_roc(L = 20)