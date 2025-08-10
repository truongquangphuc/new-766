import streamlit as st
from datetime import datetime
from utils.config import setup_page_config, load_custom_css
from utils.data_loader import load_all_data
from views.tinh_view import render_tinh_view
from views.soban_view import render_soban_view  
from views.xa_view import render_xa_view

def main():
    # Cấu hình trang
    setup_page_config()
    load_custom_css()
    
    # Header
    st.title("📊 Dashboard Theo dõi Bộ chỉ số Quyết định 766")
    st.markdown("**Bộ chỉ số chỉ đạo, điều hành và đánh giá chất lượng phục vụ người dân, doanh nghiệp**")
    st.divider()
    
    # Sidebar - Bộ lọc chung
    # Sidebar - Bộ lọc chung
    with st.sidebar:
        st.header("⚙️ Bộ lọc")
        
        # Chọn năm
        # year = st.selectbox("Chọn năm", ["2025", "2024", "2023"], index=0)
        
        # Chọn tỉnh
        tinh_options = {
            "11358": "An Giang"
        }
        selected_tinh = st.selectbox("Chọn tỉnh/thành phố", 
                                    list(tinh_options.keys()), 
                                    format_func=lambda x: tinh_options[x])
        
        # Lấy tháng và năm hiện tại
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Chọn kỳ báo cáo
        # report_type = st.radio("Kỳ báo cáo", ["Cả năm", "6 tháng", "Theo quý", "Theo tháng"])
        report_type = st.radio("Kỳ báo cáo", ["Theo tháng"])


        # Khởi tạo tham số thời gian với giá trị mặc định
        p_6thang, p_quy, p_thang = 0, 0, 0
        
        if report_type == "Theo tháng":
            # Tháng mặc định là tháng hiện tại
            p_thang = st.selectbox(
                "Chọn tháng", 
                list(range(1, 13)),
                index=current_month - 2  # index = tháng - 1
            )
            
            # Năm cho báo cáo theo tháng
            year = st.selectbox(
                "Chọn năm",
                list(range(2020, current_year + 2)),  # từ 2020 đến 2 năm sau
                index=list(range(2020, current_year + 2)).index(current_year)
            )
            
        # elif report_type == "Cả năm":
        #     # Năm mặc định là năm hiện tại
        #     year = st.selectbox(
        #         "Chọn năm",
        #         list(range(2020, current_year + 2)),
        #         index=list(range(2020, current_year + 2)).index(current_year)
        #     )
        # Xử lý tham số thời gian dựa trên lựa chọn
        # if report_type == "6 tháng":
        #     period_value = st.selectbox("Chọn 6 tháng", [1], format_func=lambda x: f"6 tháng đầu năm")
        #     p_6thang = period_value  # Gán giá trị được chọn
        # elif report_type == "Theo quý":
        #     p_quy = st.selectbox("Chọn quý", [1, 2, 3, 4])
        # elif report_type == "Theo tháng":
        #     p_thang = st.selectbox("Chọn tháng", list(range(1, 13)))
        # Trường hợp "Cả năm" giữ nguyên giá trị mặc định (0, 0, 0)
        
        # Nút refresh
        if st.button("🔄 Cập nhật dữ liệu", use_container_width=True):
            st.cache_data.clear()
            st.rerun()  # Thêm rerun để cập nhật lại toàn bộ app

    # Load dữ liệu
    with st.spinner("🔄 Đang tải dữ liệu..."):
        data = load_all_data(year, selected_tinh, p_6thang, p_quy, p_thang)
 
    
    if not data:
        st.error("❌ Không thể tải dữ liệu. Vui lòng thử lại.")
        st.stop()
    
    # Tạo 3 tabs và render views
    tab1, tab2, tab3 = st.tabs(["🏛️ TỈNH", "🏢 SỞ BAN NGÀNH", "🏘️ CẤP XÃ"])
    
    with tab1:
        render_tinh_view(data, tinh_options.get(selected_tinh, selected_tinh))
    
    with tab2:
        render_soban_view(data)
    
    with tab3:
        render_xa_view(data)
    
    # Footer
    st.divider()
    st.markdown(f"""
    <div style='text-align: center; color: gray; margin-top: 50px;'>
        <p>📊 Dashboard theo dõi Quyết định 766/QĐ-TTg | Cập nhật: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
        <p>Dữ liệu được đồng bộ từ API dichvucong.gov.vn</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
