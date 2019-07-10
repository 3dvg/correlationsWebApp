import matplotlib.pyplot as plt
import io
import base64


def build_graph(data):
    img = io.BytesIO()
    plt.plot(data)
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)


def build_complexgraph(data0, data1, data2, pct, corr):
    fig, ax1 = plt.subplots()
    ax1.plot(data1, 'b-', label='Correlated')

    followup_c = 'b-'
    if pct > 0.0:
        followup_c = 'g-'
    elif pct < 0.0:
        followup_c = 'r-'
    else:
        followup_c = 'b-'

    ax1.plot(data2, followup_c, label='Follow-up')
    ax1.yaxis.set_label_position("left")
    ax1.set_ylabel('Correlated and Follow Up')
    ax1.set_xlabel('N days')
    ax1.grid(False)

    ax2 = ax1.twinx()
    ax2.plot(data0, 'k--', label='Current')
    ax2.yaxis.set_label_position("right")
    ax2.set_ylabel('Current')
    ax2.grid(False)
    axx = plt.gca()
    fig.legend(bbox_to_anchor=(1, 0.22), bbox_transform=axx.transAxes)

    plt.title('Correlation {}'.format(corr))
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)
