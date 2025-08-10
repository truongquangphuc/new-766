import streamlit as st
from get_tthc_ketqua import (
    get_tthc_data, 
    get_yearly_summary_data, 
    get_monthly_summary_data,
    get_diem_tonghop,
    get_tthc_tilexulyhs,
    get_xuhuongdiem_data_sorted,
    get_xuhuongdiem_chiso,
    get_tinh_766_report,
    get_tinh_766_report_filtered
)

@st.cache_data(ttl=300)  # Cache 5 phút
def load_all_data(year, tinh_id, p_6thang, p_quy, p_thang):    
    """Load tất cả dữ liệu cần thiết"""
    try:
        data = {}
        
        # Load dữ liệu từ các API
        data['tthc'] = get_tthc_data(year, tinh_id, "0", p_6thang, p_quy, p_thang)
        data['yearly_summary'] = get_yearly_summary_data(year, tinh_id)
        data['monthly_summary'] = get_monthly_summary_data(
            p_nam=year,
            p_tinh_id=tinh_id, 
            p_thang=p_thang
        )
        data['diem_tonghop'] = get_diem_tonghop(year, tinh_id)
        data['tilexuly'] = get_tthc_tilexulyhs(year, tinh_id, "0", p_6thang, p_quy, p_thang)
        data['xuhuong'] = get_xuhuongdiem_data_sorted(year, tinh_id, "0", p_6thang, p_quy, p_thang)
        data['chiso'] = get_xuhuongdiem_chiso(year, tinh_id, "0", p_6thang, p_quy, p_thang)
        data['report_766'] = get_tinh_766_report(year, "398126", p_6thang, p_quy, p_thang)
        data['766_report_filtered_so_nganh'] = get_tinh_766_report_filtered(year, "398126", p_6thang, p_quy, p_thang, capdonviid="1")
        
        data['766_report_filtered_xa'] = get_tinh_766_report_filtered(
            p_nam=year,
            p_tinh_id=tinh_id,
            p_6thang=p_6thang,
            p_quy=p_quy,
            p_thang=p_thang,
            capdonviid=2
        )

        return data
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu: {e}")
        return None

def format_number(number, decimal_places=0):
    """Format số với dấu chấm phân cách"""
    if number is None:
        return "0"
    return f"{int(number):,}".replace(',', '.') if decimal_places == 0 else f"{float(number):,.{decimal_places}f}".replace(',', '.')
