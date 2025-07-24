import streamlit as st
from TTHC_fetcher import fetch_TTHC_data
from .common import show_df_pretty, plot_pie_charts

def show():
    st.subheader("1. Tổng quan tình hình cung cấp DVC & TTHC", divider='rainbow')
    data = fetch_TTHC_data()
    if data:
        with st.expander("Xem bảng dữ liệu thô"):
            show_df_pretty(data, height=320)
        plot_pie_charts(data)
    else:
        st.warning("Không có dữ liệu DVC/TTHC.")
