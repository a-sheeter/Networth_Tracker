import matplotlib
matplotlib.use("Agg") # required for Flask

import matplotlib.pyplot as plt
import io
import base64

# Pie chart
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

# Line chart
def networth_line_chart(months, values):
    fig, ax = plt.subplots()

    ax.plot(months, values)
    ax.set_xlabel("Month")
    ax.set_ylabel("Net Worth")
    ax.set_title("Net Worth Over Time")
    ax.tick_params(axis="x", rotation=45)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return base64.b64encode(buf.read()).decode("utf-8")
