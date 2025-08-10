import streamlit as st
from datetime import datetime, date
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
from get_tthc_chitiet import get_report, get_report_online, get_digitization_by_agency  # Import hàm get_report

def calculate_date_range(year, p_thang):
    """Tính toán from_date và to_date dựa trên năm và tháng"""
    if p_thang == 0:  # Nếu là cả năm
        from_date = f"{year}-01-01"
        to_date = f"{year}-12-31"
    else:  # Nếu là theo tháng cụ thể
        # Tính ngày cuối tháng
        if p_thang in [1, 3, 5, 7, 8, 10, 12]:
            last_day = 31
        elif p_thang in [4, 6, 9, 11]:
            last_day = 30
        else:  # Tháng 2
            # Kiểm tra năm nhuận
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                last_day = 29
            else:
                last_day = 28
        
        from_date = f"{year}-{p_thang:02d}-01"
        to_date = f"{year}-{p_thang:02d}-{last_day}"
    
    return from_date, to_date

@st.cache_data(ttl=300)  # Cache 5 phút
def load_all_data(year, tinh_id, p_6thang, p_quy, p_thang):
    """Load tất cả dữ liệu cần thiết"""
    try:
        data = {}
        
        # Tính toán from_date và to_date
        from_date, to_date = calculate_date_range(year, p_thang)
        
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
        data['766_report_filtered_so_nganh'] = get_tinh_766_report_filtered(
            year, "398126", p_6thang, p_quy, p_thang, capdonviid="1"
        )
        data['766_report_filtered_xa'] = get_tinh_766_report_filtered(year, "398126", p_6thang, p_quy, p_thang, capdonviid="2")
        
        # Thêm báo cáo tổng hợp KGG
        data['report_chitiet'] = get_report(
            from_date=from_date,
            to_date=to_date,
            agency_id="6852c2f06d65221a70e5b26b"
        )

        # Thêm báo cáo hồ sơ online KGG
        data['report_chitiet_online'] = get_report_online(
            from_date=from_date,
            to_date=to_date,
            agency_id="6852c2f06d65221a70e5b26b"
        )

        # Thêm báo cáo hồ sơ online KGG
        data['report_digitization'] = get_digitization_by_agency(
            from_date=from_date,
            to_date=to_date,
            ancestor_id="6852c2f06d65221a70e5b26b"
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
