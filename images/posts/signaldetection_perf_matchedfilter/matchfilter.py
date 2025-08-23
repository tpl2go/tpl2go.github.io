import numpy as np
from scipy.stats import ncx2, expon
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def simulate(snr, L=1):
    nc = 2*snr*L
    N = 10000
    y0 = (np.random.randn(N,L) + 1j * np.random.randn(N,L))/np.sqrt(L)
    sig = np.ones((N,L), dtype=np.complex128)
    y1 = np.sqrt(snr*2/L) * sig + y0

    q2_0 = np.square(np.abs(np.sum(y0*sig,axis=1)))
    q2_1 = np.square(np.abs(np.sum(y1*sig,axis=1)))

    # maxq2 = np.quantile(q2_1,0.99)
    maxq2 = ncx2.ppf(0.99, 2, nc)

    x_q2 = np.linspace(0,maxq2, 10000)
    pdf_1= ncx2.pdf(x_q2, 2, nc)
    pdf_0 = expon.pdf(x_q2, loc=0, scale=2)

    return x_q2, maxq2, pdf_0, pdf_1, q2_0, q2_1

def plot_distribution(snr, L):
    fig, ax0 =  plt.subplots(figsize=(10,5))
    ax1 = ax0.twinx()

    x_q2, maxq2, pdf_0, pdf_1, q2_0, q2_1 = simulate(snr, L)

    color = 'b'
    ax0.plot(x_q2, pdf_0,color=color, lw=2)
    ax0.hist(q2_0, bins=100, density=True, facecolor=color, alpha=0.4, label='H0 case: No signal present')
    ax0.set_ylabel('pdf (No Signal Present)')
    ax1.spines['left'].set_color(color)
    ax0.tick_params(axis='y', colors=color)
    ax0.yaxis.label.set_color(color)

    color = 'orange'
    ax1.plot(x_q2, pdf_1, color=color,  lw=2,  label='ncx2 pdf')
    ax1.hist(q2_1, bins=100, density=True, facecolor=color, alpha=0.4, label='H1 case: Signal present')
    ax1.set_ylabel('pdf (Signal Present)')
    ax1.spines['right'].set_color(color)
    ax1.tick_params(axis='y', colors=color)
    ax1.yaxis.label.set_color(color)

    ax0.set_xlabel('q^2')
    ax0.set_xlim(0, maxq2)

    plt.show()

plot_distribution(5,5)


def animate_distribution(L=3):
    fig, ax0 =  plt.subplots()
    ax1 = ax0.twinx()

    def update(snr):
        ax0.clear()
        ax1.clear()

        x_q2, maxq2, pdf_0, pdf_1, q2_0, q2_1 = simulate(snr, L)
        color = 'b'
        ax0.plot(x_q2, pdf_0,color=color, lw=2)
        ax0.hist(q2_0, bins=100, density=True, facecolor=color, alpha=0.4, label='H0 case: No signal present')
        # ax0.set_ylabel('pdf (No Signal Present)')
        ax1.spines['left'].set_color(color)
        ax0.tick_params(axis='y', colors=color)
        ax0.yaxis.label.set_color(color)

        color = 'orange'
        ax1.plot(x_q2, pdf_1, color=color,  lw=2)
        ax1.hist(q2_1, bins=100, density=True, facecolor=color, alpha=0.4, label='H1 case: Signal present')
        # ax1.set_ylabel('pdf (Signal Present)')
        ax1.spines['right'].set_color(color)
        ax1.tick_params(axis='y', colors=color)
        ax1.yaxis.label.set_color(color)

        ax0.set_xlabel('q^2')
        ax0.set_xlim(0, maxq2)

        ax0.set_ylim(0, 1.1*np.max(pdf_0))
        ax1.set_ylim(0, 1.1*np.max(pdf_1))

        ax0.set_title(f'Distribution of q^2 with signal L={L}, signal SNR={10*np.log10(snr):0.2f} dB')

        # legend on the right
        ax0.legend(loc='upper left')
        ax1.legend(loc='upper right')

        print(snr)

    ani = animation.FuncAnimation(fig, update, frames=np.linspace(1, 10, 100), interval=150)
    ani.save(f'q2distribution_L_{L}.gif', writer='pillow', dpi=50)


# animate_distribution(L=3)
# animate_distribution(L=10)


def generate_roc_curve(L=1):
    fig = plt.figure()
    for snrdb in [-6,-3,0,3,6]:
        snr = 10**(snrdb/10)
        # x_q2, maxq2, pdf_0, pdf_1, q2_0, q2_1 = simulate(snr, L)
        # print(np.square(snr*2), maxq2)
        maxq2 = max(14, np.square(snr*3))
        x_q2 = np.linspace(0,maxq2, 10000)

        tpr = 1-ncx2.cdf(x_q2, 2, 2*L*snr)
        fpr = 1-expon.cdf(x_q2, loc=0, scale=2)

        plt.plot(fpr, tpr, alpha=0.6, label=f'{snrdb} dB')
    plt.legend()
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC curves of matched filter signal detector (L={L})')
    plt.savefig(f'matchfilter_roc_L_{L}.png')
    plt.show()

generate_roc_curve(L=3)
generate_roc_curve(L=10)