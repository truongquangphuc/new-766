import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ---- MAPPING tên cột tiếng Việt ----
COLUMN_NAME_MAP = {
    "ID": "Mã đơn vị",
    "TEN": "Tên đơn vị",
    "TEN_COQUAN": "Tên cơ quan",
    "MA_COQUAN": "Mã CQ",
    "LOAI_COQUAN": "Loại đơn vị",
    "CAPDONVIID": "Cấp đơn vị",
    "ID_COQUAN": "Mã CQ (chi tiết)",
    "TDGQ": "Tiến độ giải quyết",
    "MDHL": "Mức độ hài lòng",
    "MDSH": "Số hóa hồ sơ",
    "TTTT": "Thanh toán trực tuyến",
    "CLGQ": "Dịch vụ công trực tuyến",
    "CKMB": "Công khai minh bạch",
    "TONG_SCORE": "Tổng điểm",
    "ROW_STT": "STT"
}

FIELDS_MAPPING = [
    ("MDHL", "Mức độ hài lòng"),
    ("MDSH", "Số hoá hồ sơ"),
    ("TTTT", "Thanh toán trực tuyến"),
    ("CLGQ", "Dịch vụ công trực tuyến"),
    ("CKMB", "Công khai, minh bạch"),
    ("TDGQ", "Tiến độ giải quyết"),
]

def filter_units_by_loai_coquan(units, loai):
    return [unit for unit in units if str(unit.get("LOAI_COQUAN")) == str(loai)]

def show_df_pretty(data, height=320):
    df_show = pd.DataFrame(data)
    columns_to_keep = [
        "ID", "TEN", "LOAI_COQUAN", "CAPDONVIID",
        "TDGQ", "MDHL", "MDSH", "TTTT", "CLGQ", "CKMB", "TONG_SCORE"
    ]
    columns_exist = [col for col in columns_to_keep if col in df_show.columns]
    if columns_exist:
        df_show = df_show[columns_exist]
    else:
        st.warning("Không có cột nào trong danh sách cần hiển thị!")
    df_show = df_show.rename(columns=COLUMN_NAME_MAP)
    st.dataframe(df_show, use_container_width=True, height=height)

def plot_units_barchart(units, field, field_name, top_n=10):
    df = pd.DataFrame(units)
    df[field] = pd.to_numeric(df[field], errors='coerce')
    df = df.dropna(subset=[field])
    df_bottom = df.sort_values(field, ascending=True).head(top_n)
    names = df_bottom['TEN'].str.replace('UBND ', '', regex=False)
    scores = df_bottom[field]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.barh(names, scores, color='#d62728')
    ax.set_xlabel('Điểm số')
    ax.set_title(f'Top {top_n} đơn vị có "{field_name}" thấp nhất')
    ax.invert_yaxis()
    ax.bar_label(bars, fmt='%.2f', padding=4)
    plt.tight_layout()
    st.pyplot(fig)
    st.caption(f"Top {top_n} đơn vị có '{field_name}' thấp nhất.")

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

def plot_766_barchart(title, result, standard):
    fields = [
        "Công khai, minh bạch",
        "Tiến độ giải quyết",        
        "Thanh toán trực tuyến",
        "Dịch vụ công trực tuyến",
        "Mức độ hài lòng",
        "Số hóa hồ sơ"
    ]
    import numpy as np
    angiang_scores = [result.get(field, 0) for field in fields]
    standard_scores = [standard.get(field, 0) for field in fields]
    x = np.arange(len(fields))
    width = 0.34
    fig, ax = plt.subplots(figsize=(7, 3.8))
    rects1 = ax.bar(x - width/2, angiang_scores, width, label=title, color='#1f77b4', edgecolor='white', linewidth=1.5)
    rects2 = ax.bar(x + width/2, standard_scores, width, label='Điểm chuẩn', color='#ff7f0e', edgecolor='white', linewidth=1.5)
    ax.set_ylabel('Điểm số', fontsize=11)
    ax.set_title('So sánh các chỉ số 766: '+title+' vs. Điểm chuẩn', fontsize=10, color='#0099FF')
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
