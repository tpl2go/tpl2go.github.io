import numpy as np
from scipy.stats import ncx2, expon
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def simulate(snr, L=1):
    nc = 2*snr*L

    sim_0 = np.random.randn(10000) + 1j * np.random.randn(10000)
    sim_1 = np.sqrt(snr*2) + sim_0
    # Compute q^2
    q2_0 = np.real(sim_0 * sim_0.conj())
    q2_1 = np.real(sim_1 * sim_1.conj())

    # maxq2 = np.quantile(q2_1,0.99)
    maxq2 = ncx2.ppf(0.99, 2, nc)

    x = np.linspace(0,maxq2, 10000)
    y1= ncx2.pdf(x, 2, nc)
    y0 = expon.pdf(x, loc=0, scale=2)

    return x,maxq2, y0, y1, q2_0, q2_1

def plot_distribution(snr):
    fig, ax0 =  plt.subplots(figsize=(10,5))
    ax1 = ax0.twinx()

    x, maxq2, y0, y1, q2_0, q2_1 = simulate(snr)

    color = 'b'
    ax0.plot(x, y0,color=color, lw=2)
    ax0.hist(q2_0, bins=100, density=True, facecolor=color, alpha=0.4, label='H0 case: No signal present')
    ax0.set_ylabel('pdf (No Signal Present)')
    ax1.spines['left'].set_color(color)
    ax0.tick_params(axis='y', colors=color)
    ax0.yaxis.label.set_color(color)

    color = 'orange'
    ax1.plot(x, y1, color=color,  lw=2,  label='ncx2 pdf')
    ax1.hist(q2_1, bins=100, density=True, facecolor=color, alpha=0.4, label='H1 case: Signal present')
    ax1.set_ylabel('pdf (Signal Present)')
    ax1.spines['right'].set_color(color)
    ax1.tick_params(axis='y', colors=color)
    ax1.yaxis.label.set_color(color)

    ax0.set_xlabel('q^2')
    ax0.set_xlim(0, maxq2)

    plt.show()



def animate_distribution():
    fig, ax0 =  plt.subplots()
    ax1 = ax0.twinx()

    def update(snr):
        ax0.clear()
        ax1.clear()

        x, maxq2, y0, y1, q2_0, q2_1 = simulate(snr)
        color = 'b'
        ax0.plot(x, y0,color=color, lw=2)
        ax0.hist(q2_0, bins=100, density=True, facecolor=color, alpha=0.4, label='H0 case: No signal present')
        # ax0.set_ylabel('pdf (No Signal Present)')
        ax1.spines['left'].set_color(color)
        ax0.tick_params(axis='y', colors=color)
        ax0.yaxis.label.set_color(color)

        color = 'orange'
        ax1.plot(x, y1, color=color,  lw=2)
        ax1.hist(q2_1, bins=100, density=True, facecolor=color, alpha=0.4, label='H1 case: Signal present')
        # ax1.set_ylabel('pdf (Signal Present)')
        ax1.spines['right'].set_color(color)
        ax1.tick_params(axis='y', colors=color)
        ax1.yaxis.label.set_color(color)

        ax0.set_xlabel('q^2')
        ax0.set_xlim(0, maxq2)

        ax0.set_ylim(0, 1.1*np.max(y0))
        ax1.set_ylim(0, 1.1*np.max(y1))

        ax0.set_title(f'Distribution of q^2 with signal L=1, signal SNR={10*np.log10(snr):0.2f} dB')

        # legend on the right
        ax0.legend(loc='upper left')
        ax1.legend(loc='upper right')

        print(snr)

    ani = animation.FuncAnimation(fig, update, frames=np.linspace(1, 10, 100), interval=150)
    ani.save('q2distribution.gif', writer='pillow')


# animate_distribution()

fig = plt.figure()
for snrdb in [0,3,6,9,12]:
    snr = 10**(snrdb/10)
    x, maxq2, y0, y1, q2_0, q2_1 = simulate(snr)

    tpr = 1-ncx2.cdf(x, 2, 2*snr)
    fpr = 1-expon.cdf(x, loc=0, scale=2)

    plt.plot(fpr, tpr, alpha=0.6, label=f'{snrdb} dB')
plt.legend()
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC curves of matched filter signal detector (L=1)')
plt.savefig('matchfilter_roc.png')
plt.show()