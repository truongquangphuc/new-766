import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from TTHC_fetcher import fetch_TTHC_data
from CS766_fetcher import fetch_766_data

# ---- Cài đặt Streamlit Page config ----
st.set_page_config(
    page_title="Dashboard DVC & Chỉ số 766",
    page_icon=":bar_chart:",
    layout="wide"
)

# ---- Title and Intro ----
st.markdown(
    """
    <h1 style='color:#0099FF; font-size: 2.4rem; margin-bottom:0.5rem;'>Báo cáo trực quan Dịch vụ công & Chỉ số 766</h1>
    <p style='font-size:1.1rem; color:#666; margin-bottom:2rem;'>
        Nguồn dữ liệu cập nhật tự động từ <a href='https://dichvucong.gov.vn' target='_blank'>Cổng DVCQG</a>.<br>
        Dashboard này giúp bạn <b>so sánh hiệu quả cung cấp dịch vụ công</b> và theo dõi <b>các chỉ số trọng yếu</b> của tỉnh An Giang.
    </p>
    """, unsafe_allow_html=True
)

# ---- Pie Chart Function ----
def plot_pie_charts(data):
    df = pd.DataFrame(data)
    numerical_columns = [
        'Số TTHC',
        'Số TTHC đủ điều kiện cung cấp DVC toàn trình',
        'Số TTHC đã cung cấp DVC trực tuyến toàn trình',
        'Số TTHC đã cung cấp DVC trực tuyến một phần',
        'Số TTHC chưa cung cấp DVCTT'
    ]
    df[numerical_columns] = df[numerical_columns].apply(pd.to_numeric, errors='coerce')

    # Pie Chart 1
    total_tthc = df['Số TTHC'].sum()
    available_tthc = df['Số TTHC đủ điều kiện cung cấp DVC toàn trình'].sum()
    remaining_tthc = total_tthc - available_tthc
    labels1 = ['Đủ điều kiện DVC toàn trình', 'Chưa đủ điều kiện']
    sizes1 = [available_tthc, remaining_tthc]

    def func(pct, allvalues):
        absolute = int(round(pct / 100. * sum(allvalues), 0))
        return f"{absolute}\n({pct:.1f}%)"

    fig1, ax1 = plt.subplots()
    ax1.pie(
        sizes1, labels=labels1, autopct=lambda pct: func(pct, sizes1), startangle=90,
        colors=['#1f77b4', '#a6cee3'], textprops={'color': "black", "fontsize":12}
    )
    ax1.axis('equal')
    ax1.set_title('Tỉ lệ TTHC đủ điều kiện cung cấp DVC toàn trình', fontsize=15, color='#0099FF')

    # Pie Chart 2
    sizes2 = [
        df['Số TTHC đã cung cấp DVC trực tuyến toàn trình'].sum(),
        df['Số TTHC đã cung cấp DVC trực tuyến một phần'].sum(),
        df['Số TTHC chưa cung cấp DVCTT'].sum()
    ]
    labels2 = ['DVC toàn trình', 'DVC một phần', 'Chưa cung cấp']

    fig2, ax2 = plt.subplots()
    ax2.pie(
        sizes2, labels=labels2, autopct=lambda pct: func(pct, sizes2), startangle=90,
        colors=['#33a02c', '#b2df8a', '#fb9a99'], textprops={'color': "black", "fontsize":12}
    )
    ax2.axis('equal')
    ax2.set_title('Phân loại mức độ DVC trực tuyến', fontsize=15, color='#33a02c')

    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(fig1)
        st.caption("Biểu đồ 1: Tỉ lệ TTHC đủ điều kiện cung cấp DVC toàn trình.")
    with col2:
        st.pyplot(fig2)
        st.caption("Biểu đồ 2: Tỉ lệ mức độ cung cấp DVC trực tuyến.")

# ---- Bar Chart Function ----
def plot_766_barchart(result, standard):
    fields = [
        "Công khai, minh bạch",
        "Tiến độ giải quyết",
        "Dịch vụ công trực tuyến",
        "Thanh toán trực tuyến",
        "Mức độ hài lòng",
        "Số hóa hồ sơ"
    ]
    angiang_scores = [result.get(field, 0) for field in fields]
    standard_scores = [standard.get(field, 0) for field in fields]
    x = np.arange(len(fields))
    width = 0.34

    fig, ax = plt.subplots(figsize=(7, 3.8))
    rects1 = ax.bar(x - width/2, angiang_scores, width, label='An Giang', color='#1f77b4', edgecolor='white', linewidth=1.5)
    rects2 = ax.bar(x + width/2, standard_scores, width, label='Điểm chuẩn', color='#ff7f0e', edgecolor='white', linewidth=1.5)

    ax.set_ylabel('Điểm số', fontsize=11)
    ax.set_title('So sánh các chỉ số 766: An Giang vs. Điểm chuẩn', fontsize=10, color='#0099FF')
    ax.set_xticks(x)
    ax.set_xticklabels(fields, rotation=15, fontsize=9)
    ax.legend(fontsize=8, loc='upper center', frameon=False)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.spines[['top','right']].set_visible(False)
    ax.bar_label(rects1, padding=2, fontsize=8, fmt='%.2f')
    ax.bar_label(rects2, padding=2, fontsize=8, fmt='%.2f')
    plt.tight_layout()

    col1, _ = st.columns([3, 2])
    with col1:
        st.pyplot(fig)
        st.caption("Các chỉ số càng gần hoặc vượt chuẩn càng tốt. Điểm thấp cần lưu ý cải thiện.")

# ---- Main Display Function ----
def display_data():
    with st.container():
        st.subheader("1. Tổng quan tình hình cung cấp DVC & TTHC", divider='rainbow')
        data = fetch_TTHC_data()
        if data:
            with st.expander("Xem bảng dữ liệu thô"):
                st.dataframe(pd.DataFrame(data), use_container_width=True, height=320)
            plot_pie_charts(data)
        else:
            st.warning("Không có dữ liệu DVC/TTHC.")

    with st.container():
        st.subheader("2. Chỉ số 766: So sánh tỉnh An Giang với điểm chuẩn", divider='rainbow')
        data_766 = fetch_766_data("398126")
        if data_766 and "target" in data_766:
            with st.expander("Xem chi tiết chỉ số 766 của An Giang"):
                st.dataframe(
                    pd.DataFrame([data_766["target"]]),
                    use_container_width=True,
                    hide_index=True,
                )
                if "raw" in data_766:
                    st.json(data_766["raw"], expanded=False)
            st.markdown("---")
            standard = {
                "Công khai, minh bạch": 18,
                "Tiến độ giải quyết": 20,
                "Dịch vụ công trực tuyến": 12,
                "Thanh toán trực tuyến": 10,
                "Mức độ hài lòng": 18,
                "Số hóa hồ sơ": 22
            }
            plot_766_barchart(data_766["target"], standard)
        else:
            st.error("Không có dữ liệu chỉ số 766 của An Giang.")

if __name__ == "__main__":
    display_data()
