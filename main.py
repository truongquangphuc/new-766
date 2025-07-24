import streamlit as st
from views import overview_show, cs766_show, unit_compare_show

st.set_page_config(
    page_title="Dashboard DVC & Chỉ số 766",
    page_icon=":bar_chart:",
    layout="wide"
)

st.markdown(
    """
    <h1 style='color:#0099FF; font-size: 2.4rem; margin-bottom:0.5rem;'>Báo cáo trực quan Dịch vụ công & Chỉ số 766</h1>
    <p style='font-size:1.1rem; color:#666; margin-bottom:2rem;'>
        Nguồn dữ liệu cập nhật tự động từ <a href='https://dichvucong.gov.vn' target='_blank'>Cổng DVCQG</a>.<br>
        Dashboard này giúp bạn <b>so sánh hiệu quả cung cấp dịch vụ công</b> và theo dõi <b>các chỉ số trọng yếu</b> của tỉnh An Giang.
    </p>
    """, unsafe_allow_html=True
)

def display_data():
    overview_show()
    cs766_show()
    unit_compare_show()

if __name__ == "__main__":
    display_data()
