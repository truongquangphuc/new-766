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

# ---- Function: Pie Charts ----
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
    labels = ['Đủ điều kiện DVC toàn trình', 'Chưa đủ điều kiện']
    sizes = [available_tthc, remaining_tthc]

    def func(pct, allvalues):
        absolute = int(round(pct / 100. * sum(allvalues), 0))
        return f"{absolute}\n({pct:.1f}%)"

    fig1, ax1 = plt.subplots()
    wedges, texts, autotexts = ax1.pie(
        sizes, labels=labels, autopct=lambda pct: func(pct, sizes), startangle=90,
        colors=['#1f77b4', '#a6cee3'], textprops={'color': "black", "fontsize":12}
    )
    ax1.axis('equal')
    ax1.set_title('Tỉ lệ TTHC đủ điều kiện cung cấp DVC toàn trình', fontsize=15, color='#0099FF')
    plt.setp(autotexts, size=11, weight="bold")
    plt.setp(texts, size=12)

    # Pie Chart 2
    online_full_tthc = df['Số TTHC đã cung cấp DVC trực tuyến toàn trình'].sum()
    online_partial_tthc = df['Số TTHC đã cung cấp DVC trực tuyến một phần'].sum()
    offline_tthc_3 = df['Số TTHC chưa cung cấp DVCTT'].sum()
    labels3 = ['DVC toàn trình', 'DVC một phần', 'Chưa cung cấp']
    sizes3 = [online_full_tthc, online_partial_tthc, offline_tthc_3]

    fig2, ax2 = plt.subplots()
    wedges2, texts2, autotexts2 = ax2.pie(
        sizes3, labels=labels3, autopct=lambda pct: func(pct, sizes3), startangle=90,
        colors=['#33a02c', '#b2df8a', '#fb9a99'], textprops={'color': "black", "fontsize":12}
    )
    ax2.axis('equal')
    ax2.set_title('Phân loại mức độ DVC trực tuyến', fontsize=15, color='#33a02c')
    plt.setp(autotexts2, size=11, weight="bold")
    plt.setp(texts2, size=12)

    # Layout: Pie charts song song
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(fig1)
        st.caption("Biểu đồ 1: Tỉ lệ TTHC đủ điều kiện cung cấp DVC toàn trình.")
    with col2:
        st.pyplot(fig2)
        st.caption("Biểu đồ 2: Tỉ lệ mức độ cung cấp DVC trực tuyến.")

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
    width = 0.34

    fig, ax = plt.subplots(figsize=(6, 3.5))  # Cỡ vừa đẹp cho dashboard và đủ chỗ cho nhãn

    rects1 = ax.bar(x - width/2, angiang_scores, width, label='An Giang', color='#1f77b4', edgecolor='white', linewidth=1.5)
    rects2 = ax.bar(x + width/2, standard_scores, width, label='Điểm chuẩn', color='#ff7f0e', edgecolor='white', linewidth=1.5)

    ax.set_ylabel('Điểm số', fontsize=11)
    ax.set_title('So sánh các chỉ số 766: An Giang vs. Điểm chuẩn', fontsize=10, color='#0099FF')
    ax.set_xticks(x)
    ax.set_xticklabels(fields, rotation=12, fontsize=9)
    ax.legend(fontsize=6, loc='upper center', frameon=False)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.spines[['top','right']].set_visible(False)
    ax.bar_label(rects1, padding=2, fontsize=8, fmt='%.2f')
    ax.bar_label(rects2, padding=2, fontsize=8, fmt='%.2f')
    plt.tight_layout()

    # Đặt biểu đồ vào cột lớn (chiếm 60%) để không bị nhỏ quá
    col1, _ = st.columns([3, 2])   # col1 to hơn, col2 chỉ để trống hoặc caption
    with col1:
        st.pyplot(fig)
        st.caption("Các chỉ số càng gần hoặc vượt chuẩn càng tốt. Điểm thấp cần lưu ý cải thiện.")


# ---- Main Display Function ----
def display_data():
    # TTHC DATA & Pie Chart section
    with st.container():
        st.subheader("1. Tổng quan tình hình cung cấp DVC & TTHC", divider='rainbow')
        data = fetch_TTHC_data()
        if data:
            with st.expander("Xem bảng dữ liệu thô"):
                st.dataframe(pd.DataFrame(data), use_container_width=True, height=320)
            plot_pie_charts(data)
        else:
            st.warning("Không có dữ liệu DVC/TTHC.")

    # 766 DATA & Bar Chart section
    with st.container():
        st.subheader("2. Chỉ số 766: So sánh tỉnh An Giang với điểm chuẩn", divider='rainbow')
        target_id = "398126"
        data_766 = fetch_766_data(target_id)
        if data_766:
            cols = st.columns([1,2])
            with cols[0]:
                st.markdown("#### Thông tin chi tiết An Giang")
                styled_df = pd.DataFrame([data_766]).style\
                    .background_gradient(cmap='Blues', subset=["Tổng điểm"])\
                    .set_properties(**{'font-size': '14px'})
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            with cols[1]:
                st.json(data_766, expanded=False)
            st.markdown("---")
            standard = {
                "Công khai, minh bạch": 18,
                "Tiến độ giải quyết": 20,
                "Dịch vụ trực tuyến": 10,
                "Mức độ hài lòng": 18,
                "Số hóa hồ sơ": 22
            }
            plot_766_barchart(data_766, standard)
        else:
            st.error("Không có dữ liệu chỉ số 766 của An Giang.")

if __name__ == "__main__":
    display_data()
