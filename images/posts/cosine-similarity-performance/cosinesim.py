import numpy as np
from scipy.stats import beta,ncx2, expon
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sklearn import metrics

def simulate(snr, L=100):
    N = 10**5
    sim_0 = np.random.randn(N, L) + 1j * np.random.randn(N, L)
    sig = np.ones_like(sim_0)
    sim_1 = np.sqrt(snr*2) * sig + sim_0

    # Compute q^2
    signorm2 = np.square(np.linalg.norm(sig, axis=1))
    q2_0 = np.square(np.abs(np.sum(sim_0 * sig.conj(), axis=1)))/np.square(np.linalg.norm(sim_0, axis=1))/signorm2
    q2_1 = np.square(np.abs(np.sum(sim_1 * sig.conj(), axis=1)))/np.square(np.linalg.norm(sim_1, axis=1))/signorm2

    return q2_0, q2_1

def plot_distribution(snr,L=50):
    

    q2_0, q2_1 = simulate(snr, L)
    print(beta.fit(q2_0, floc=0, fscale=1))
    print(beta.fit(q2_1, floc=0, fscale=1))

    fig, ax0 =  plt.subplots(figsize=(10,5))
    ax1 = ax0.twinx()

    color = 'b'
    x_qf2 = np.linspace(0, 1, 1000)
    ax0.plot(x_qf2, beta.pdf(x_qf2, 1,L-1), color=color)
    ax0.hist(q2_0, bins=100, density=True, facecolor=color, alpha=0.4, label='H0 case: No signal present')
    ax0.set_ylabel('pdf (No Signal Present)')
    ax1.spines['left'].set_color(color)
    ax0.tick_params(axis='y', colors=color)
    ax0.yaxis.label.set_color(color)

    color = 'orange'
    print("mean of signal q^2",np.mean(q2_1), snr/(1+snr))
    ax0.plot(x_qf2, beta.pdf(x_qf2, snr*L,L*snr/(snr+1)), color=color)
    ax0.hist(q2_1, bins=100, density=True, facecolor=color, alpha=0.4, label='H1 case: Signal present')
    ax0.set_ylabel('pdf (Signal Present)')
    ax0.spines['right'].set_color(color)
    ax0.tick_params(axis='y', colors=color)
    ax0.yaxis.label.set_color(color)

    ax0.axvline(snr/(snr+1), color='k', ls='--')

    ax0.set_xlabel('q^2')
    ax0.set_xlim(0, 1)

    plt.show()

# investigate relationship between L and alpha beta
# plt.figure()
# for i, snr in enumerate([1,1.5, 2]):
#     alphas, betas = [], []
#     theoryalphas, theorybetas = [], []
#     Ls = np.arange(2,50)
#     for L in Ls:
#         q2_0, q2_1 = simulate(snr, L)
#         a, b,_,_ = beta.fit(q2_1, floc=0, fscale=1)
#         alphas.append(a)
#         betas.append(b)
#         ta = snr*L*snr/(snr+1)
#         tb = L*snr/(snr+1)
#         theoryalphas.append(ta)
#         theorybetas.append(tb)
#         print(f"L={L:02d}, alpha={a:0.3f}, theory alpha={ta:0.3f}, beta={b:0.3f}, theory beta={tb:0.3f} , deltabeta = {tb/b:0.3f} ")



#     plt.plot(Ls, np.array(alphas)/Ls, color=f"C{i}", label='alpha')
#     # plt.plot(Ls, theoryalphas, color="C0", linestyle='--')
#     plt.plot(Ls, np.array(betas)/Ls, linestyle='--', color=f"C{i}",label='betas')
#     # plt.plot(Ls, theorybetas, color="C1", linestyle='--')
# plt.show()

# investigate relationship between beta slope and snr
# plt.figure()
# snrs = np.arange(1,20)
# betafactor = []
# for snr in snrs:
#     q2_0, q2_1 = simulate(snr, L=50)
#     a, b,_,_ = beta.fit(q2_1, floc=0, fscale=1)
#     betafactor.append(b/50)
# plt.plot(snrs, np.array(betafactor))
# plt.xlabel('SNR')
# plt.ylabel('beta slope')
# plt.show()


# for snr in range(1,20):
#     plot_distribution(snr,L=3)



def animate_distribution(L = 3):
    fig, ax0 =  plt.subplots()
    ax1 = ax0.twinx()

    def update(snr):
        ax0.clear()
        ax1.clear()

        q2_0, q2_1 = simulate(snr, L)
        a0,b0, _, _ = beta.fit(q2_0, floc=0, fscale=1)
        a1,b1, _, _ = beta.fit(q2_1, floc=0, fscale=1)

        eps = 1e-6
        x_q2 = np.linspace(eps, 1-eps, 1000)
        pdf0 = beta.pdf(x_q2, a0, b0)
        pdf1 = beta.pdf(x_q2, a1, b1)

        color = 'b'
        ax0.plot(x_q2, pdf0,color=color, lw=2)
        ax0.hist(q2_0, bins=100, density=True, facecolor=color, alpha=0.4, label='H0 case: No signal present')
        # ax0.set_ylabel('pdf (No Signal Present)')
        ax1.spines['left'].set_color(color)
        ax0.tick_params(axis='y', colors=color)
        ax0.yaxis.label.set_color(color)

        color = 'orange'
        ax1.plot(x_q2, pdf1, color=color,  lw=2)
        ax1.hist(q2_1, bins=100, density=True, facecolor=color, alpha=0.4, label='H1 case: Signal present')
        # ax1.set_ylabel('pdf (Signal Present)')
        ax1.spines['right'].set_color(color)
        ax1.tick_params(axis='y', colors=color)
        ax1.yaxis.label.set_color(color)

        ax0.set_xlabel('q^2')
        ax0.set_xlim(0, 1)

        ax0.set_ylim(0, 1.1*np.max(pdf0))
        ax1.set_ylim(0, 1.1*np.max(pdf1))

        ax0.set_title(f'Distribution of cosine similarity q^2 with signal L={L}, signal SNR={10*np.log10(snr):0.2f} dB')

        # legend on the right
        ax0.legend(loc='upper left')
        ax1.legend(loc='upper right')

        print(snr)

    ani = animation.FuncAnimation(fig, update, frames=np.linspace(1, 10, 100), interval=150)
    ani.save(f'q2distribution_L_{L}.gif', writer='pillow')


# animate_distribution(L=3)
# animate_distribution(L=10)


def plot_roc(L=3):
    fig = plt.figure()
    for snrdb in [-6,-3,0,3,6]:
        snr = 10**(snrdb/10)
        q2_0, q2_1 = simulate(snr, L)
        y_true = np.concatenate([np.zeros_like(q2_0), np.ones_like(q2_1)])
        scores = np.concatenate([q2_0, q2_1])
        fpr, tpr, thresholds = metrics.roc_curve(y_true, scores)
        plt.plot(fpr, tpr, alpha=0.6, label=f'{snrdb} dB')
    plt.legend()
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC curves of matched filter signal detector (L={L})')
    plt.savefig(f'matchfilter_roc_L_{L}.png')
    plt.show()

# plot_roc(L=3)
# plot_roc(L=10)


def compare_roc(L=3):
    fig = plt.figure()
    for i, snrdb in enumerate([-6,-3,0,3,6]):
        snr = 10**(snrdb/10)
        q2_0, q2_1 = simulate(snr, L)
        y_true = np.concatenate([np.zeros_like(q2_0), np.ones_like(q2_1)])
        scores = np.concatenate([q2_0, q2_1])
        fpr, tpr, thresholds = metrics.roc_curve(y_true, scores)
        plt.plot(fpr, tpr, color=f"C{i}", alpha=0.6, label=f'CosineSim {snrdb} dB')

        maxq2 = max(14, np.square(snr*3))
        x_q2 = np.linspace(0,maxq2, 10000)

        tpr = 1-ncx2.cdf(x_q2, 2, L*snr)
        fpr = 1-expon.cdf(x_q2, loc=0, scale=2)

        plt.plot(fpr, tpr, color=f"C{i}", linestyle='--', alpha=0.6, label=f'MatchFilter {snrdb} dB')

        
    plt.legend()
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'Comparing ROC of two signal detectors (L={L})')
    plt.savefig(f'compare_roc_L_{L}.png')
    plt.show()

compare_roc(L=3)
compare_roc(L=10)
compare_roc(L=30)