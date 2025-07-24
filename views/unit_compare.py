import streamlit as st
from CS766_fetcher import fetch_766_all_units_in_province
from .common import filter_units_by_loai_coquan, show_df_pretty, plot_units_barchart, FIELDS_MAPPING

def show():
    st.subheader("3. So sánh các chỉ số giữa các đơn vị trong tỉnh An Giang", divider='rainbow')
    units = fetch_766_all_units_in_province("398126")
    if units:
        with st.expander("Xem toàn bộ các đơn vị trong tỉnh"):
            show_df_pretty(units, height=400)
        so_ban_nganh = filter_units_by_loai_coquan(units, 2)
        st.markdown("#### Sở, ban, ngành")
        if so_ban_nganh:
            show_df_pretty(so_ban_nganh, height=320)
            plot_units_barchart(so_ban_nganh, field="TONG_SCORE", field_name="Tổng điểm", top_n=10)
            for field, field_name in FIELDS_MAPPING:
                plot_units_barchart(so_ban_nganh, field=field, field_name=field_name, top_n=5)
        else:
            st.warning("Không có dữ liệu sở, ban, ngành.")
        xa_phuong = filter_units_by_loai_coquan(units, 3)
        st.markdown("#### Xã, phường, đặc khu")
        if xa_phuong:
            show_df_pretty(xa_phuong, height=320)
            plot_units_barchart(xa_phuong, field="TONG_SCORE", field_name="Tổng điểm", top_n=10)
            for field, field_name in FIELDS_MAPPING:
                plot_units_barchart(xa_phuong, field=field, field_name=field_name, top_n=10)
        else:
            st.warning("Không có dữ liệu xã/phường/đặc khu.")
    else:
        st.error("Không có dữ liệu các đơn vị trong tỉnh An Giang.")
