# streamlit_app.py - Version đã sửa lỗi
import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from get_tthc_chitiet import get_report

# Cấu hình trang
st.set_page_config(
    page_title="📊 Dashboard Thủ Tục Hành Chính", 
    page_icon="📊",
    layout="wide"
)

# CSS tùy chỉnh
st.markdown("""
<style>
.metric-container {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 10px;
    border-left: 5px solid #1f77b4;
}
.big-font {
    font-size: 24px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Tiêu đề chính
st.title("📊 Dashboard Thủ Tục Hành Chính")

# Sidebar để nhập thông tin
st.sidebar.header("🔧 Cấu hình truy vấn")

# Input fields
start_date = st.sidebar.date_input(
    "📅 Từ ngày",
    value=date(2024, 7, 1)
)

end_date = st.sidebar.date_input(
    "📅 Đến ngày", 
    value=date(2024, 7, 31)
)

agency_id = st.sidebar.text_input(
    "🏢 Agency ID",
    value="6852c2f06d65221a70e5b26b"
)

# Nút truy vấn
if st.sidebar.button("🔍 Truy vấn dữ liệu", type="primary"):
    if agency_id.strip():
        with st.spinner("⏳ Đang tải dữ liệu..."):
            try:
                # Chuyển đổi định dạng ngày
                start_str = start_date.strftime("%Y-%m-%d")
                end_str = end_date.strftime("%Y-%m-%d")
                
                # Gọi API
                result = get_report(start_str, end_str, agency_id)
                
                if result:
                    st.session_state.data = result
                    st.session_state.query_info = {
                        'start_date': start_str,
                        'end_date': end_str,
                        'agency_id': agency_id,
                        'total_records': len(result)
                    }
                    st.success(f"✅ Thành công! Tải được {len(result)} bản ghi")
                else:
                    st.error("❌ Không có dữ liệu")
                    
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
    else:
        st.sidebar.error("⚠️ Vui lòng nhập Agency ID")

# Hiển thị dữ liệu nếu có
if 'data' in st.session_state and st.session_state.data:
    data = st.session_state.data
    query_info = st.session_state.query_info
    
    # Thông tin truy vấn
    st.info(f"📊 Hiển thị {query_info['total_records']} bản ghi từ {query_info['start_date']} đến {query_info['end_date']}")
    
    # Chuyển đổi sang DataFrame và xử lý cột agency
    df = pd.DataFrame(data)
    
    # ✅ SỬA LỖI: Trích xuất thông tin agency thành các cột riêng biệt
    df['agency_id'] = df['agency'].apply(lambda x: x.get('id', 'N/A') if isinstance(x, dict) else 'N/A')
    df['agency_name'] = df['agency'].apply(lambda x: x.get('name', 'N/A') if isinstance(x, dict) else 'N/A')
    df['agency_code'] = df['agency'].apply(lambda x: x.get('code', 'N/A') if isinstance(x, dict) else 'N/A')
    
    # Tổng quan
    st.header("📈 Tổng quan")
    
    # Tính toán các metrics tổng
    total_received = df['received'].sum()
    total_resolved = df['resolved'].sum()
    total_unresolved = df['unresolved'].sum()
    total_cancelled = df['cancelled'].sum()
    
    # Hiển thị metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📥 Tổng nhận", 
            value=f"{total_received:,}",
            help="Tổng số hồ sơ được tiếp nhận"
        )
    
    with col2:
        st.metric(
            label="✅ Đã giải quyết", 
            value=f"{total_resolved:,}",
            delta=f"{total_resolved/total_received*100:.1f}%" if total_received > 0 else "0%",
            help="Tổng số hồ sơ đã được giải quyết"
        )
    
    with col3:
        st.metric(
            label="⏳ Chưa giải quyết", 
            value=f"{total_unresolved:,}",
            delta=f"{total_unresolved/total_received*100:.1f}%" if total_received > 0 else "0%",
            help="Tổng số hồ sơ chưa được giải quyết"
        )
    
    with col4:
        st.metric(
            label="🚫 Đã hủy", 
            value=f"{total_cancelled:,}",
            help="Tổng số hồ sơ đã bị hủy"
        )
    
    # Charts
    st.header("📊 Biểu đồ phân tích")
    
    # Tạo tabs cho các loại biểu đồ
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Tổng quan", "🏢 Theo cơ quan", "⏰ Tiến độ xử lý", "🌐 Kênh tiếp nhận"])
    
    with tab1:
        # Biểu đồ tròn tổng quan
        if total_received > 0:
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Đã giải quyết', 'Chưa giải quyết', 'Đã hủy'],
                values=[total_resolved, total_unresolved, total_cancelled],
                hole=.3,
                marker_colors=['#2E8B57', '#FFA500', '#DC143C']
            )])
            
            fig_pie.update_layout(
                title="Tình trạng xử lý hồ sơ",
                font=dict(size=14)
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Không có dữ liệu để hiển thị biểu đồ")
    
    with tab2:
        # ✅ SỬA LỖI: Sử dụng agency_name thay vì agency dictionary
        if len(df) > 0:
            # Nhóm theo tên cơ quan
            agency_data = df.groupby('agency_name').agg({
                'received': 'sum',
                'resolved': 'sum',
                'unresolved': 'sum'
            }).reset_index()
            
            # Sắp xếp theo số hồ sơ nhận được
            agency_data = agency_data.sort_values('received', ascending=True).tail(10)
            
            if len(agency_data) > 0 and agency_data['received'].sum() > 0:
                fig_bar = px.bar(
                    agency_data, 
                    x='received', 
                    y='agency_name',
                    orientation='h',
                    title="Top 10 cơ quan có nhiều hồ sơ nhất",
                    labels={'received': 'Số hồ sơ', 'agency_name': 'Cơ quan'}
                )
                
                fig_bar.update_layout(height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Không có dữ liệu cơ quan để hiển thị")
        else:
            st.info("Không có dữ liệu để hiển thị")
    
    with tab3:
        # Biểu đồ tiến độ xử lý
        early_resolved = df['resolvedEarly'].sum()
        ontime_resolved = df['resolvedOnTime'].sum()
        overdue_resolved = df['resolvedOverdue'].sum()
        ontime_unresolved = df['unresolvedOnTime'].sum()
        overdue_unresolved = df['unresolvedOverdue'].sum()
        
        if (early_resolved + ontime_resolved + overdue_resolved + ontime_unresolved + overdue_unresolved) > 0:
            progress_data = {
                'Loại': ['Sớm hạn', 'Đúng hạn', 'Quá hạn'],
                'Đã giải quyết': [early_resolved, ontime_resolved, overdue_resolved],
                'Chưa giải quyết': [0, ontime_unresolved, overdue_unresolved]
            }
            
            fig_progress = go.Figure()
            fig_progress.add_trace(go.Bar(
                name='Đã giải quyết',
                x=progress_data['Loại'],
                y=progress_data['Đã giải quyết'],
                marker_color='#2E8B57'
            ))
            fig_progress.add_trace(go.Bar(
                name='Chưa giải quyết',
                x=progress_data['Loại'],
                y=progress_data['Chưa giải quyết'],
                marker_color='#FFA500'
            ))
            
            fig_progress.update_layout(
                title="Tiến độ xử lý hồ sơ",
                xaxis_title="Loại tiến độ",
                yaxis_title="Số lượng",
                barmode='stack'
            )
            
            st.plotly_chart(fig_progress, use_container_width=True)
        else:
            st.info("Không có dữ liệu tiến độ để hiển thị")
    
    with tab4:
        # Kênh tiếp nhận
        online_total = df['receivedOnline'].sum()
        direct_total = df['receivedDirect'].sum()
        
        if online_total > 0 or direct_total > 0:
            channel_data = {
                'Kênh': ['Trực tuyến', 'Trực tiếp'],
                'Số lượng': [online_total, direct_total]
            }
            
            fig_channel = px.pie(
                channel_data,
                values='Số lượng',
                names='Kênh',
                title="Phân bố theo kênh tiếp nhận"
            )
            
            st.plotly_chart(fig_channel, use_container_width=True)
        else:
            st.info("Không có dữ liệu về kênh tiếp nhận")
    
    # Bảng dữ liệu chi tiết
    st.header("📋 Dữ liệu chi tiết")
    
    # ✅ SỬA LỖI: Sử dụng các cột đã trích xuất thay vì dictionary
    # Chọn các cột cần thiết
    columns_to_show = [
        'agency_name', 'agency_code', 'received', 'resolved', 'unresolved', 
        'resolvedEarly', 'resolvedOnTime', 'resolvedOverdue',
        'receivedOnline', 'receivedDirect'
    ]
    
    # Đổi tên cột
    column_mapping = {
        'agency_name': 'Tên cơ quan',
        'agency_code': 'Mã cơ quan',
        'received': 'Tổng nhận',
        'resolved': 'Đã giải quyết',
        'unresolved': 'Chưa giải quyết',
        'resolvedEarly': 'Giải quyết sớm',
        'resolvedOnTime': 'Giải quyết đúng hạn',
        'resolvedOverdue': 'Giải quyết trễ hạn',
        'receivedOnline': 'Tiếp nhận online',
        'receivedDirect': 'Tiếp nhận trực tiếp'
    }
    
    final_df = df[columns_to_show].rename(columns=column_mapping)
    
    # Hiển thị bảng với khả năng tìm kiếm
    st.dataframe(
        final_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Nút download
    csv = final_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="💾 Tải xuống CSV",
        data=csv,
        file_name=f"bao_cao_tthc_{query_info['start_date']}_to_{query_info['end_date']}.csv",
        mime="text/csv"
    )

else:
    # Hiển thị khi chưa có dữ liệu
    st.info("👈 Vui lòng nhập thông tin và nhấn 'Truy vấn dữ liệu' để bắt đầu")
    
    # Hiển thị ví dụ
    with st.expander("💡 Ví dụ cách sử dụng"):
        st.write("""
        **Các bước thực hiện:**
        1. 📅 Chọn khoảng thời gian cần truy vấn
        2. 🏢 Nhập Agency ID (ví dụ: 6852c2f06d65221a70e5b26b)
        3. 🔍 Nhấn nút "Truy vấn dữ liệu"
        4. 📊 Xem kết quả trên dashboard
        
        **Ý nghĩa các chỉ số:**
        - **Tổng nhận**: Tổng số hồ sơ được tiếp nhận
        - **Đã giải quyết**: Số hồ sơ đã được xử lý xong
        - **Chưa giải quyết**: Số hồ sơ đang trong quá trình xử lý
        - **Đã hủy**: Số hồ sơ bị hủy bỏ
        """)

# Footer
st.markdown("---")
st.markdown("*Dashboard được tạo bằng Streamlit • Dữ liệu cập nhật real-time*")
