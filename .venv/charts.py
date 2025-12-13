import matplotlib
matplotlib.use("Agg") # required for Flask

import matplotlib.pyplot as plt
import io
import base64

def networth_pie_chart(assets_total, liabilities_total):
    labels = ["Assets", "Liabilities"]
    values = [assets_total, liabilities_total]
    colors =["green", "red"]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return image_base64
