import streamlit as st
import pandas as pd
from CS766_fetcher import fetch_766_angiang_info
from .common import plot_766_barchart, show_df_pretty

def show():
    st.subheader("2. Chỉ số 766: So sánh tỉnh An Giang với điểm chuẩn", divider='rainbow')
    data_766 = fetch_766_angiang_info("398126")
    if data_766 and "target" in data_766:
        with st.expander("Xem chi tiết chỉ số 766 của An Giang"):
            st.dataframe(
                pd.DataFrame([data_766["target"]]),
                use_container_width=True,
                hide_index=True,
            )
            if "raw" in data_766:
                show_df_pretty([data_766["raw"]], height=100)
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
