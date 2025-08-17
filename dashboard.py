import streamlit as st
from datetime import datetime

from utils.config import setup_page_config, load_custom_css
from utils.data_loader import load_all_data, calculate_date_range, KGGDataLoader

from views.tinh_view import render_tinh_view
from views.soban_view import render_soban_view, SoBanTableRenderer
from views.xa_view import render_xa_view
from get_tthc_chitiet import APIClient as KGGAPIClient

@st.cache_data(ttl=300)
def load_kgg_data(from_date: str, to_date: str):
    client = KGGAPIClient()
    loader = KGGDataLoader(client)
    chitiet = loader.get_kgg_report(from_date, to_date)
    online = loader.get_kgg_online_report(from_date, to_date)
    digit = loader.get_digitization_report(from_date, to_date)
    return chitiet, online, digit

def main():
    setup_page_config()
    load_custom_css()

    # --- SIDEBAR BỘ LỌC ---
    with st.sidebar:
        st.header("⚙️ Bộ lọc")

        current_year = datetime.now().year
        current_month = datetime.now().month
        years = [str(y) for y in range(current_year, current_year - 5, -1)]
        default_year_index = 0

        year = st.selectbox("Chọn năm", years, index=default_year_index)
        tinh_options = {"11358": "An Giang"}
        selected_tinh = st.selectbox(
            "Chọn tỉnh/thành phố",
            list(tinh_options.keys()),
            format_func=lambda x: tinh_options[x]
        )

        # Default tháng/quý/6 tháng
        if current_month == 1:
            default_month = 12
            default_year_for_month = str(current_year - 1)
        else:
            default_month = current_month - 1
            default_year_for_month = str(current_year)

        # radio_options = ["Cả năm", "6 tháng", "Theo quý", "Theo tháng"]
        radio_options = ["Cả năm", "Theo tháng"]
        report_type = st.radio("Kỳ báo cáo", radio_options, index=1)

        p_6thang, p_quy, p_thang = 0, 0, 0
        if report_type == "6 tháng":
            p_6thang = st.selectbox("Chọn 6 tháng", [1], format_func=lambda x: "6 tháng đầu năm")
            
        elif report_type == "Theo quý":
            p_quy = st.selectbox("Chọn quý", [1, 2, 3, 4])
            
        elif report_type == "Theo tháng":
            months = list(range(1, 13))
            if year == default_year_for_month:
                default_month_index = default_month - 1
            else:
                default_month_index = 0
            p_thang = st.selectbox("Chọn tháng", months, index=default_month_index)

        # Xác định chuỗi mô tả cho bộ lọc
        if report_type == "Cả năm":
            filter_info = f"📅 Hiển thị dữ liệu cho cả năm {year}"
        elif report_type == "Theo tháng":
            filter_info = f"📅 Hiển thị dữ liệu cho tháng {p_thang}/{year}"
        elif report_type == "Theo quý":
            filter_info = f"📅 Hiển thị dữ liệu cho quý {p_quy}/{year}"
        elif report_type == "6 tháng":
            filter_info = f"📅 Hiển thị dữ liệu cho 6 tháng đầu năm {year}"
        else:
            filter_info = ""

        if st.button("🔄 Cập nhật dữ liệu", use_container_width=True):
            st.cache_data.clear()
            st.session_state.clear()
            st.experimental_rerun()

    # Header
    st.title("📊 Dashboard Theo dõi Bộ chỉ số 766 tỉnh An Giang")
    st.markdown("**Quyết định số 766/QĐ-TTg của Thủ tướng Chính phủ: Phê duyệt Bộ chỉ số chỉ đạo, điều hành và đánh giá chất lượng phục vụ người dân, doanh nghiệp trong thực hiện thủ tục hành chính, dịch vụ công theo thời gian thực trên môi trường điện tử**")
    st.info(filter_info)   # 👈 Dòng thông báo lọc kỳ báo cáo
    st.divider()

    # --- TẢI DỮ LIỆU DCV QUỐC GIA ---
    with st.spinner("🔄 Đang tải dữ liệu quốc gia..."):
        year_int = int(year)
        data = load_all_data(year_int, selected_tinh, p_6thang, p_quy, p_thang)
        if not data:
            st.error("❌ Không thể tải dữ liệu. Vui lòng thử lại.")
            st.stop()

    # --- TABS GIAO DIỆN ---
    tab1, tab2, tab3 = st.tabs(["🏛️ TỈNH", "🏢 SỞ BAN NGÀNH", "🏘️ CẤP XÃ"])

    from_date, to_date = calculate_date_range(year_int, p_thang)

    with tab1:
        render_tinh_view(data, tinh_options.get(selected_tinh, selected_tinh))

    with tab2:
        st.header("🔥 Số liệu Quốc gia (Cổng DVCQG)")
        render_soban_view(data, from_date, to_date)
        st.divider()

    with tab3:
        st.header("🔥 Số liệu Quốc gia (Cổng DVCQG)")
        render_xa_view(data, from_date, to_date)
        st.divider()

    # Footer
    st.markdown(
        f"""
        📊 Dashboard theo dõi Quyết định 766/QĐ-TTg | Cập nhật: {datetime.now().strftime("%d/%m/%Y %H:%M")}
        Dữ liệu được đồng bộ từ API dichvucong.gov.vn và An Giang
        """
    )

if __name__ == "__main__":
    main()
