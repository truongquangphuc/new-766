import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from TTHC_fetcher import fetch_TTHC_data  # Import the data fetching function
from CS766_fetcher import fetch_766_data  # Import the 766 fetch function

# Function to plot Pie charts with counts and percentages
def plot_pie_charts(data):
    df = pd.DataFrame(data)
    numerical_columns = ['Số TTHC', 'Số TTHC đủ điều kiện cung cấp DVC toàn trình', 
                         'Số TTHC đã cung cấp DVC trực tuyến toàn trình', 
                         'Số TTHC đã cung cấp DVC trực tuyến một phần', 
                         'Số TTHC chưa cung cấp DVCTT']
    for column in numerical_columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # Pie Chart 1
    total_tthc = df['Số TTHC'].sum()
    available_tthc = df['Số TTHC đủ điều kiện cung cấp DVC toàn trình'].sum()
    remaining_tthc = total_tthc - available_tthc
    labels = ['TTHC đủ điều kiện cung cấp DVC toàn trình', 'Chưa đủ điều kiện']
    sizes = [available_tthc, remaining_tthc]

    def func(pct, allvalues):
        absolute = round(pct / 100.*sum(allvalues), 0)
        return f"{absolute} ({pct:.1f}%)"

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct=lambda pct: func(pct, sizes), startangle=90, colors=['#66b3ff','#99ff99'])
    ax1.axis('equal')
    ax1.set_title('Số TTHC ' + str(total_tthc))

    # Pie Chart 2
    online_full_tthc = df['Số TTHC đã cung cấp DVC trực tuyến toàn trình'].sum()
    online_partial_tthc = df['Số TTHC đã cung cấp DVC trực tuyến một phần'].sum()
    offline_tthc_3 = df['Số TTHC chưa cung cấp DVCTT'].sum()
    labels3 = ['DVC trực tuyến toàn trình', 'DVC trực tuyến một phần', 'DVC chưa cung cấp']
    sizes3 = [online_full_tthc, online_partial_tthc, offline_tthc_3]

    fig3, ax3 = plt.subplots()
    ax3.pie(sizes3, labels=labels3, autopct=lambda pct: func(pct, sizes3), startangle=90, colors=['#ff99cc','#ffcc99','#ff6666'])
    ax3.axis('equal')
    ax3.set_title('Phân chia DVC: Toàn trình, Một phần và Chưa cung cấp')

    st.pyplot(fig1)
    st.pyplot(fig3)

# Bar chart for 766 index comparison
def plot_766_barchart(result, standard):
    fields = [
        "Công khai, minh bạch",
        "Tiến độ giải quyết",
        "Dịch vụ trực tuyến",
        "Mức độ hài lòng",
        "Số hóa hồ sơ"
    ]
    angiang_scores = [result[field] for field in fields]
    standard_scores = [standard[field] for field in fields]

    x = np.arange(len(fields))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    rects1 = ax.bar(x - width/2, angiang_scores, width, label='An Giang', color='#0099FF')
    rects2 = ax.bar(x + width/2, standard_scores, width, label='Điểm chuẩn', color='#FF9933')

    ax.set_ylabel('Điểm số')
    ax.set_title('So sánh các chỉ số 766: An Giang vs. Điểm chuẩn')
    ax.set_xticks(x)
    ax.set_xticklabels(fields, rotation=20)
    ax.legend()
    ax.bar_label(rects1, padding=3, fmt='%.2f')
    ax.bar_label(rects2, padding=3, fmt='%.2f')

    plt.tight_layout()
    st.pyplot(fig)

def display_data():
    # --- TTHC DATA ---
    data = fetch_TTHC_data()
    if data:
        # st.title("DVC Data from Website")
        # st.write("### Dữ liệu thô")
        # st.write(data)
        # st.write("### Dữ liệu JSON")
        # st.json(data)
        st.write("### Biểu đồ TTHC")
        plot_pie_charts(data)
    else:
        st.write("No data found.")

    # --- 766 DATA ---
    st.title("So sánh chỉ số 766 của tỉnh An Giang với điểm chuẩn")
    target_id = "398126"
    data_766 = fetch_766_data(target_id)

    if data_766:
        # st.write("### Chỉ số 766 của tỉnh An Giang (chuẩn hóa key)")
        # st.dataframe(pd.DataFrame([data_766]))
        # st.json(data_766)
        standard = {
            "Công khai, minh bạch": 18,
            "Tiến độ giải quyết": 20,
            "Dịch vụ trực tuyến": 10,
            "Mức độ hài lòng": 18,
            "Số hóa hồ sơ": 22
        }
        st.write("### Biểu đồ bar so sánh chỉ số 766")
        plot_766_barchart(data_766, standard)
    else:
        st.error("Không có dữ liệu chỉ số 766 của An Giang")

if __name__ == "__main__":
    display_data()
