import streamlit as st
import pandas as pd
import plotly.express as px
from utils.config import CHART_COLORS


def render_xa_view(data):
    if not data['766_report_filtered_xa']:
        st.info("Không có dữ liệu TTHC chi tiết")
        return
        
    tthc_data = data['766_report_filtered_xa']

    if tthc_data:
        # Tạo selectbox để chọn xã
        def format_tthc_option(item):
            return f"{item['TEN']} (MA_COQUAN: {item['MA_COQUAN']})"
        
        # Tạo danh sách options
        tthc_options = [format_tthc_option(item) for item in tthc_data]
        
        selected_option = st.selectbox(
            "🏢 Chọn xã để xem báo cáo:",
            options=tthc_options,
            index=0,
            help="Chọn đơn vị để xem báo cáo chi tiết 766",
            key="xa_selector"
        )
        
        # Lấy thông tin của item được chọn
        selected_index = tthc_options.index(selected_option)
        selected_tthc = tthc_data[selected_index]
        
        # Sử dụng cho các xử lý tiếp theo
        selected_tthc_id = selected_tthc['MA_COQUAN']
        selected_tthc_name = selected_tthc['TEN']
        
    else:
        st.warning("⚠️ Không có dữ liệu xã để hiển thị")
        return

    # Hiển thị chỉ số 766 theo format yêu cầu
    st.subheader(f"{selected_tthc_name}", divider='rainbow')
    
    # Lấy dữ liệu chỉ số 766 từ data['report_766']
    if 'report_766' in data and data['report_766']:
        # Tìm item tương ứng với selected_tthc_id
        item = next((item for item in data['report_766'] if item['MA_COQUAN'] == selected_tthc_id), None)
        
        if not item:
            st.error(f"Không tìm thấy dữ liệu chỉ số 766 cho {selected_tthc_name}")
            return
        
        # Chuẩn hóa trường theo format yêu cầu
        target = {
            "Công khai, minh bạch": float(item.get('CKMB', 0)),
            "Tiến độ giải quyết": float(item.get('TDGQ', 0)),
            "Dịch vụ công trực tuyến": float(item.get('CLGQ', 0)),
            "Thanh toán trực tuyến": float(item.get('TTTT', 0)),
            "Mức độ hài lòng": float(item.get('MDHL', 0)),
            "Số hóa hồ sơ": float(item.get('MDSH', 0)),
            "Điểm tổng": float(item.get('TONG_SCORE', 0)),
        }
        
        result = {"target": target, "raw": item}
        
        if result and "target" in result:
            # Điểm chuẩn theo QĐ 766
            standard = {
                "Công khai, minh bạch": 18,
                "Tiến độ giải quyết": 20,
                "Dịch vụ công trực tuyến": 12,
                "Thanh toán trực tuyến": 10,
                "Mức độ hài lòng": 18,
                "Số hóa hồ sơ": 22
            }
            
            # Tạo biểu đồ so sánh với điểm chuẩn
            _plot_766_barchart(selected_tthc_name.split(' - ')[0], result["target"], standard)
        else:
            st.error(f"Không có dữ liệu chỉ số 766 của {selected_tthc_name}")
    else:
        st.warning("⚠️ Không có dữ liệu report_766")

    # THÊM MỚI: Hiển thị báo cáo chi tiết KGG
    _render_chitiet_report(data, selected_tthc_id, selected_tthc_name)
    _render_chitiet_report_online(data, selected_tthc_id, selected_tthc_name)
    _render_digitization_report(data, selected_tthc_id, selected_tthc_name)


def _render_chitiet_report(data, selected_tthc_id, selected_tthc_name):
    """Hiển thị báo cáo chi tiết KGG"""
    
    st.subheader(f"📋 Kết quả xử lý hồ sơ trên một cửa điện tử: {selected_tthc_name}", divider='blue')
    
    if 'report_chitiet' not in data or not data['report_chitiet']:
        st.warning("⚠️ Không có dữ liệu báo cáo chi tiết")
        return
    
    chitiet_data = data['report_chitiet']
    
    # 🔥 LỌC DỮ LIỆU THEO CODE
    filtered_data = []
    debug_info = []  # Để debug
    
    for item in chitiet_data:
        # Kiểm tra cấu trúc dữ liệu thực tế
        agency = item.get('agency', {})
        agency_id = agency.get('id', '') if agency else ''
        agency_code = agency.get('code', '') if agency else ''
        agency_name = agency.get('name', '') if agency else ''
        
        # Debug: Thu thập thông tin để kiểm tra
        debug_info.append({
            'agency_id': agency_id,
            'agency_code': agency_code,
            'agency_name': agency_name,
            'selected_id': selected_tthc_id
        })
        
        # 🎯 CHỈ LỌC THEO CODE
        if agency_code == selected_tthc_id:
            filtered_data.append(item)
    
        
    # Hiển thị kết quả lọc
    if not filtered_data:
        st.warning(f"⚠️ Không tìm thấy dữ liệu với CODE: `{selected_tthc_id}`")
        st.info(f"💡 Hiển thị tất cả {len(chitiet_data)} bản ghi thay thế")
        filtered_data = chitiet_data
    # else:
    #     st.success(f"✅ Tìm thấy {len(filtered_data)} bản ghi với CODE: `{selected_tthc_id}`")
    
    # Hiển thị chi tiết
    _render_chitiet_detail_table(filtered_data)
 

def _render_chitiet_detail_table(data):
    """Hiển thị bảng chi tiết - chỉ số liệu"""
    
    if not data:
        st.info("Không có dữ liệu để hiển thị")
        return
    
    # Tạo DataFrame với các trường chính
    display_data = []
    for item in data:
        agency = item.get('agency', {})
        display_data.append({
            'Tên cơ quan': agency.get('name', 'N/A'),
            # 'Mã cơ quan': agency.get('code', 'N/A'),
            # 'Cấp độ': agency.get('level', 'N/A'),
            'Đã nhận': f"{item.get('received', 0):,}".replace(',', '.'),
            'Đã giải quyết': f"{item.get('resolved', 0):,}".replace(',', '.'),
            'Trực tuyến': f"{item.get('receivedOnline', 0):,}".replace(',', '.'),
            'Trực tiếp': f"{item.get('receivedDirect', 0):,}".replace(',', '.'),
            'Quá hạn': f"{item.get('resolvedOverdue', 0):,}".replace(',', '.'),
        })
    
    st.markdown('#### Thống kê tổng hợp xử lý hồ sơ')
    df = pd.DataFrame(display_data)
    
    # Hiển thị bảng
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_chitiet_report_online(data, selected_tthc_id, selected_tthc_name):
    """Hiển thị báo cáo chi tiết online KGG"""
  
    if 'report_chitiet_online' not in data or not data['report_chitiet_online']:
        st.warning("⚠️ Không có dữ liệu báo cáo chi tiết các TTHC online")
        return
    
    chitiet_data = data['report_chitiet_online']
    
    # 🔥 LỌC DỮ LIỆU THEO AGENCY_NAME
    filtered_data = []
    debug_info = []  # Để debug
    
    # 🎯 LOẠI BỎ " - tỉnh An Giang" KHỎI TÊN
    clean_selected_name = selected_tthc_name #.replace(" - tỉnh An Giang", "").strip()
    
    for item in chitiet_data:
        agency_id = item.get('agency_id', '')
        agency_name = item.get('agency_name', '')
        
        # Debug: Thu thập thông tin để kiểm tra
        debug_info.append({
            'agency_id': agency_id,
            'agency_name': agency_name,
            'selected_name': selected_tthc_name,
            'clean_selected_name': clean_selected_name
        })
        
        # 🎯 LỌC THEO AGENCY_NAME (so sánh tên đã làm sạch)
        # Lọc theo logic: clean_selected_name contains agency_name
        agency_name_lower = agency_name.lower()
        clean_selected_name_lower = clean_selected_name.lower()

        if (agency_name_lower == clean_selected_name_lower or 
            agency_name_lower in clean_selected_name_lower):
            filtered_data.append(item)

    
    # Hiển thị kết quả lọc
    if not filtered_data:
        st.warning(f"⚠️ Không tìm thấy dữ liệu với TÊN: `{clean_selected_name}`")
        st.info(f"💡 Hiển thị tất cả {len(chitiet_data)} bản ghi thay thế")
        filtered_data = chitiet_data
    
    # Hiển thị chi tiết
    _render_chitiet_online_detail_table(filtered_data)



def _render_chitiet_online_detail_table(data):
    """Hiển thị bảng chi tiết online - chỉ số liệu"""
    
    if not data:
        st.info("Không có dữ liệu để hiển thị")
        return
    
    # Tạo DataFrame với các trường mới theo cấu trúc dữ liệu mảng
    display_data = []
    for item in data:
        display_data.append({
            # 'Tên cơ quan': item.get('agency_name', 'N/A'),
            # 'Cơ quan cha': item.get('parent_name', 'N/A'),
            'Phát sinh 1 phần': f"{item.get('phatsinh_1phan_quantity', 0):,}".replace(',', '.'),
            'Phát sinh toàn phần': f"{item.get('phatsinh_toanphan_quantity', 0):,}".replace(',', '.'),
            'Chờ tiếp nhận': f"{item.get('chotiepnhan_quantity', 0):,}".replace(',', '.'),
            'Đã tiếp nhận': f"{item.get('datiepnhan_quantity', 0):,}".replace(',', '.'),
            'Hoàn thành': f"{item.get('hoanthanh_quantity', 0):,}".replace(',', '.'),
            'Từ chối': f"{item.get('tuchoi_quantity', 0):,}".replace(',', '.'),
            'Thanh toán online': f"{item.get('onlinepaid_quantity', 0):,}".replace(',', '.'),
            'Tổng cộng': f"{item.get('total', 0):,.1f}".replace(',', '.'),
        })
    
    st.markdown('#### Thống kê số liệu về hồ sơ trực tuyến')
    df = pd.DataFrame(display_data)
    
    # Hiển thị bảng
    st.dataframe(df, use_container_width=True, hide_index=True)

def _render_digitization_report(data, selected_tthc_id, selected_tthc_name):
    """Hiển thị báo cáo số hóa KGG"""
    
    if 'report_digitization' not in data or not data['report_digitization']:
        st.warning("⚠️ Không có dữ liệu báo cáo chi tiết")
        return
    
    chitiet_data = data['report_digitization']
    
    # 🔥 LỌC DỮ LIỆU THEO CODE
    filtered_data = []
    debug_info = []  # Để debug
    
    for item in chitiet_data:
        # Kiểm tra cấu trúc dữ liệu thực tế
        agency = item.get('agency', {})
        agency_id = agency.get('id', '') if agency else ''
        agency_code = agency.get('code', '') if agency else ''
        agency_name = agency.get('name', '') if agency else ''
        
        # Debug: Thu thập thông tin để kiểm tra
        debug_info.append({
            'agency_id': agency_id,
            'agency_code': agency_code,
            'agency_name': agency_name,
            'selected_id': selected_tthc_id
        })
        
        # 🎯 CHỈ LỌC THEO CODE
        if agency_code == selected_tthc_id:
            filtered_data.append(item)
    
        
    # Hiển thị kết quả lọc
    if not filtered_data:
        st.warning(f"⚠️ Không tìm thấy dữ liệu với CODE: `{selected_tthc_id}`")
        st.info(f"💡 Hiển thị tất cả {len(chitiet_data)} bản ghi thay thế")
        filtered_data = chitiet_data
    # else:
    #     st.success(f"✅ Tìm thấy {len(filtered_data)} bản ghi với CODE: `{selected_tthc_id}`")
    
    # Hiển thị chi tiết
    _render_digitization_report_table(filtered_data)
 

def _render_digitization_report_table(data):
    """Hiển thị bảng chi tiết - chỉ số liệu"""
    
    if not data:
        st.info("Không có dữ liệu để hiển thị")
        return
    
    # Tạo DataFrame với các trường chính
    display_data = []
    for item in data:
        agency = item.get('agency', {})
        display_data.append({
            'Tổng tiếp nhận': f"{item.get('totalReceiver', 0):,}".replace(',', '.'),
            'Tiếp nhận có file': f"{item.get('totalReceiverHavingFile', 0):,}".replace(',', '.'),
            'Tổng hoàn thành': f"{item.get('totalComplete', 0):,}".replace(',', '.'),
            'Hoàn thành có file': f"{item.get('totalCompleteHavingFile', 0):,}".replace(',', '.'),
            'Tiếp nhận không file': f"{item.get('totalReceiverNopeFile', 0):,}".replace(',', '.'),
            'Hoàn thành không file': f"{item.get('totalCompleteNopeFile', 0):,}".replace(',', '.'),
            'Tiếp nhận & hoàn thành có file': f"{item.get('totalReceiverCompleteHavingFile', 0):,}".replace(',', '.'),
            '% Tiếp nhận có file': f"{item.get('percentTotalReceiverHavingFile', 0):.2f}%",
            '% Hoàn thành có file': f"{item.get('percentTotalCompleteHavingFile', 0):.2f}%",
            '% Tiếp nhận & hoàn thành có file': f"{item.get('percentTotalReceiverCompleteHavingFile', 0):.2f}%"
        })

    
    st.markdown('#### Thống kê hồ sơ số hóa')
    df = pd.DataFrame(display_data)
    
    # Hiển thị bảng
    st.dataframe(df, use_container_width=True, hide_index=True)

def _plot_766_barchart(unit_name, target_data, standard_data):
    """Tạo biểu đồ so sánh chỉ số 766 với điểm chuẩn"""
    
    # Loại bỏ "Điểm tổng" khỏi comparison (vì không có trong standard)
    comparison_keys = [key for key in target_data.keys() if key != "Điểm tổng"]
    
    # Tạo DataFrame cho biểu đồ
    df_chart = pd.DataFrame({
        'Chỉ số': comparison_keys,
        'Điểm đạt được': [target_data[key] for key in comparison_keys],
        'Điểm chuẩn': [standard_data.get(key, 0) for key in comparison_keys]
    })
    
    # Chuyển sang long format
    df_melted = df_chart.melt(
        id_vars=['Chỉ số'], 
        value_vars=['Điểm đạt được', 'Điểm chuẩn'],
        var_name='Loại điểm', 
        value_name='Điểm số'
    )
    
    # Tạo biểu đồ cột nhóm
    fig = px.bar(
        df_melted,
        x='Chỉ số',
        y='Điểm số',
        color='Loại điểm',
        title=f"So sánh chỉ số 766: {unit_name} vs Điểm chuẩn",
        barmode='group',
        color_discrete_map={
            'Điểm đạt được': CHART_COLORS.get('primary', '#1f77b4'),
            'Điểm chuẩn': CHART_COLORS.get('secondary', '#ff7f0e')
        },
        text='Điểm số'
    )
    
    fig.update_layout(
        xaxis_title="Các chỉ số đánh giá",
        yaxis_title="Điểm số",
        xaxis_tickangle=-45,
        showlegend=True,
        height=500,
        title_x=0.5
    )
    
    # Hiển thị giá trị trên cột
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Hiển thị bảng so sánh
    st.subheader("📊 Bảng so sánh chi tiết")
    
    # Tính toán tỷ lệ đạt được
    df_comparison = df_chart.copy()
    df_comparison['Tỷ lệ đạt (%)'] = (df_comparison['Điểm đạt được'] / df_comparison['Điểm chuẩn'] * 100).round(1)
    df_comparison['Chênh lệch'] = (df_comparison['Điểm đạt được'] - df_comparison['Điểm chuẩn']).round(1)
    
    # Tạo cột đánh giá
    def evaluate_score(row):
        ratio = row['Tỷ lệ đạt (%)']
        if ratio >= 100:
            return "✅ Đạt chuẩn"
        elif ratio >= 80:
            return "⚠️ Gần đạt"
        else:
            return "❌ Chưa đạt"
    
    df_comparison['Đánh giá'] = df_comparison.apply(evaluate_score, axis=1)
    
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)
