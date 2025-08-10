import streamlit as st

def setup_page_config():
    """Cấu hình trang Streamlit"""
    st.set_page_config(
        page_title="Dashboard Theo dõi Quyết định 766/QĐ-TTg", 
        page_icon="📊", 
        layout="wide"
    )

def load_custom_css():
    """Load CSS tùy chỉnh"""
    st.markdown("""
    <style>
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
            background-color: #f0f2f6;
            border-radius: 10px 10px 0 0;
        }
        .section-header {
            background: linear-gradient(90deg, #1f4e79, #2e8b57);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

# Cấu hình tỉnh
TINH_OPTIONS = {
    "11358": "Hải Dương",
    "11000": "Hà Nội", 
    "398126": "Tỉnh 766",
    "12000": "TP.HCM"
}

# Màu sắc cho biểu đồ
CHART_COLORS = {
    'success': '#2E8B57',
    'warning': '#FFD700', 
    'info': '#4169E1',
    'danger': '#DC143C',
    'primary': '#1f4e79'
}
