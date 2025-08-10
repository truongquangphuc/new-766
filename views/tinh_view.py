import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.config import CHART_COLORS

def render_tinh_view(data, tinh_name):
    """Render view cấp tỉnh"""
    
    
    # Render biểu đồ xu hướng và gauge
    col1, col2 = st.columns([2, 1])
    with col1:
        _render_trend_chart(data)
    with col2:
        _render_gauge_chart(data)
    
    # Render 7 nhóm chỉ số
    _render_chi_so_766(data)

    
    st.divider()
    # Render metrics tổng quan
    _render_overview_metrics(data)
    


# Helper functions để xử lý giá trị số an toàn
def safe_number(value, default=0):
    """Chuyển đổi giá trị về số, trả về default nếu không thể chuyển đổi"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Chuyển đổi giá trị về số nguyên, trả về default nếu không thể chuyển đổi"""
    try:
        return int(float(value)) if value is not None else default
    except (ValueError, TypeError):
        return default
def _render_overview_metrics(data):
    """Render metrics tổng quan"""
    if not data['monthly_summary']:
        st.warning("Không có dữ liệu tổng hợp")
        return
    
    # Lấy dữ liệu summary
    summary = data['monthly_summary'][0]
    # ==============================================================================
    # 1. TỔNG HỢP HỒ SƠ, KẾT QUẢ XỬ LÝ
    # ==============================================================================
    st.header("📊 TỔNG HỢP HỒ SƠ, KẾT QUẢ XỬ LÝ")
    col1, col2, col3 = st.columns(3)

    with col1:
        hs_total = safe_int(summary.get('HS_TOTAL', 0))
        st.metric(
            label="📋 Tổng số hồ sơ TTHC tiếp nhận, giải quyết",
            value=f"{hs_total:,}".replace(',', '.'),
            delta=None,
            help="HS_TOTAL: Tổng số hồ sơ thủ tục hành chính (TTHC) tiếp nhận, giải quyết"
        )

    with col2:
        db_total = safe_int(summary.get('DB_TOTAL', 0))
        db_rate = (db_total / hs_total * 100) if hs_total > 0 else 0
        st.metric(
            label="☁️ Tổng số hồ sơ đồng bộ lên DVCQG",
            value=f"{db_total:,}".replace(',', '.'),
            delta=f"Tỷ lệ: {db_rate:.1f}%",
            help="DB_TOTAL: Tổng số hồ sơ đã đồng bộ lên Cổng Dịch vụ công Quốc gia"
        )

    with col3:
        tntk_total = safe_int(summary.get('TNTK_TOTAL', 0))
        st.metric(
            label="📈 Số TTHC được tính toán thống kê",
            value=f"{tntk_total:,}".replace(',', '.'),
            delta=None,
            help="TNTK_TOTAL: Tổng số thủ tục hành chính được tính toán thống kê trong kỳ báo cáo"
        )

    st.divider()

    # ==============================================================================
    # 2. HÌNH THỨC NỘP HỒ SƠ THỦ TỤC HÀNH CHÍNH
    # ==============================================================================
    st.header("📝 HÌNH THỨC NỘP HỒ SƠ THỦ TỤC HÀNH CHÍNH")

    # Row 1: Nộp trực tiếp và bưu chính
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tructiep_rate = safe_number(summary.get('HTN_TRUCTIEP', 0))
        st.metric(
            label="🏢 Tỷ lệ nộp trực tiếp",
            value=f"{tructiep_rate:.1f}%",
            help="HTN_TRUCTIEP: Tỷ lệ hồ sơ nộp trực tiếp tại bộ phận tiếp nhận"
        )

    with col2:
        tructiep_total = safe_int(summary.get('HTN_TRUCTIEP_TOTAL', 0))
        st.metric(
            label="🏢 Số lượng nộp trực tiếp",
            value=f"{tructiep_total:,}".replace(',', '.'),
            delta=f"{tructiep_rate:.1f}% tổng hồ sơ" if tructiep_rate > 0 else None,
            help="HTN_TRUCTIEP_TOTAL: Số lượng hồ sơ nộp trực tiếp"
        )

    with col3:
        buuchinh_rate = safe_number(summary.get('HTN_BUUCHINH', 0))
        st.metric(
            label="📮 Tỷ lệ nộp qua bưu chính",
            value=f"{buuchinh_rate:.1f}%",
            help="HTN_BUUCHINH: Tỷ lệ hồ sơ nộp qua bưu chính"
        )

    with col4:
        buuchinh_total = safe_int(summary.get('HTN_BUUCHINH_TOTAL', 0))
        st.metric(
            label="📮 Số lượng nộp qua bưu chính",
            value=f"{buuchinh_total:,}".replace(',', '.'),
            delta=f"{buuchinh_rate:.1f}% tổng hồ sơ" if buuchinh_rate > 0 else None,
            help="HTN_BUUCHINH_TOTAL: Số lượng hồ sơ nộp qua bưu chính"
        )

    # Row 2: Nộp trực tuyến
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tructuyen_rate = safe_number(summary.get('HTN_TRUCTUYEN', 0))
        delta_color = "normal" if tructuyen_rate >= 70 else "inverse"
        st.metric(
            label="💻 Tỷ lệ nộp trực tuyến chuẩn",
            value=f"{tructuyen_rate:.1f}%",
            delta=f"{tructuyen_rate - 70:.1f}% so với chuẩn (70%)",
            delta_color=delta_color,
            help="HTN_TRUCTUYEN: Tỷ lệ hồ sơ nộp trực tuyến (online)"
        )

    with col2:
        tructuyen_total = safe_int(summary.get('HTN_TRUCTUYEN_TOTAL', 0))
        st.metric(
            label="💻 Số lượng nộp trực tuyến chuẩn",
            value=f"{tructuyen_total:,}".replace(',', '.'),
            delta=f"{tructuyen_rate:.1f}% tổng hồ sơ" if tructuyen_rate > 0 else None,
            help="HTN_TRUCTUYEN_TOTAL: Số lượng hồ sơ nộp trực tuyến chuẩn"
        )

    with col3:
        tructuyen_kc_rate = safe_number(summary.get('HTN_TRUCTUYEN_KHONGCHUAN', 0))
        st.metric(
            label="📧 Tỷ lệ trực tuyến không chuẩn",
            value=f"{tructuyen_kc_rate:.1f}%",
            delta_color="inverse" if tructuyen_kc_rate > 10 else "normal",
            help="HTN_TRUCTUYEN_KHONGCHUAN: Tỷ lệ hồ sơ nộp trực tuyến chưa chuẩn hóa (qua email, chưa qua hệ thống chính thức)"
        )

    with col4:
        tructuyen_kc_total = safe_int(summary.get('HTN_TRUCTUYEN_KHONGCHUAN_TOTAL', 0))
        st.metric(
            label="📧 Số lượng trực tuyến không chuẩn",
            value=f"{tructuyen_kc_total:,}".replace(',', '.'),
            delta=f"{tructuyen_kc_rate:.1f}% tổng hồ sơ" if tructuyen_kc_rate > 0 else None,
            help="HTN_TRUCTUYEN_KHONGCHUAN_TOTAL: Số lượng hồ sơ nộp trực tuyến không chuẩn"
        )

    st.divider()

    # ==============================================================================
    # 3. HÌNH THỨC TRẢ KẾT QUẢ THỦ TỤC HÀNH CHÍNH
    # ==============================================================================
    st.header("📤 HÌNH THỨC TRẢ KẾT QUẢ THỦ TỤC HÀNH CHÍNH")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        htdh_rate = safe_number(summary.get('HTDH', 0))
        delta_color = "normal" if htdh_rate >= 90 else "inverse"
        st.metric(
            label="✅ Tỷ lệ trả kết quả đúng hạn",
            value=f"{htdh_rate:.1f}%",
            delta=f"{htdh_rate - 90:.1f}% so với chuẩn (90%)",
            delta_color=delta_color,
            help="HTDH: Tỷ lệ hồ sơ trả kết quả đúng hạn (so với tổng số hồ sơ đã xử lý)"
        )

    with col2:
        htdh_total = safe_int(summary.get('HTDH_TOTAL', 0))
        st.metric(
            label="✅ Số lượng trả kết quả đúng hạn",
            value=f"{htdh_total:,}".replace(',', '.'),
            delta=f"{htdh_rate:.1f}% hồ sơ đã xử lý" if htdh_rate > 0 else None,
            help="HTDH_TOTAL: Số lượng hồ sơ trả kết quả đúng hạn"
        )

    with col3:
        htqh_rate = safe_number(summary.get('HTQH', 0))
        delta_color = "inverse" if htqh_rate > 10 else "normal"
        st.metric(
            label="❌ Tỷ lệ trả kết quả quá hạn",
            value=f"{htqh_rate:.1f}%",
            delta=f"Vượt {htqh_rate:.1f}% giới hạn" if htqh_rate > 10 else f"Dưới giới hạn 10%",
            delta_color=delta_color,
            help="HTQH: Tỷ lệ hồ sơ trả kết quả quá hạn"
        )

    with col4:
        htqh_total = safe_int(summary.get('HTQH_TOTAL', 0))
        st.metric(
            label="❌ Số lượng trả kết quả quá hạn",
            value=f"{htqh_total:,}".replace(',', '.'),
            delta=f"{htqh_rate:.1f}% hồ sơ đã xử lý" if htqh_rate > 0 else None,
            delta_color="inverse" if htqh_total > 0 else "normal",
            help="HTQH_TOTAL: Số lượng hồ sơ trả kết quả quá hạn"
        )

    st.divider()

    # ==============================================================================
    # 4. KẾT QUẢ XỬ LÝ
    # ==============================================================================
    st.header("⚡ KẾT QUẢ XỬ LÝ")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        dxlth_rate = safe_number(summary.get('DXLTH', 0))
        delta_color = "normal" if dxlth_rate >= 95 else "inverse"
        st.metric(
            label="✅ Tỷ lệ xử lý đúng hạn",
            value=f"{dxlth_rate:.1f}%",
            delta=f"{dxlth_rate - 95:.1f}% so với chuẩn (95%)",
            delta_color=delta_color,
            help="DXLTH: Tỷ lệ hồ sơ xử lý đúng hạn (%)"
        )

    with col2:
        dxlth_total = safe_int(summary.get('DXLTH_TOTAL', 0))
        st.metric(
            label="✅ Số lượng xử lý đúng hạn",
            value=f"{dxlth_total:,}".replace(',', '.'),
            delta=f"{dxlth_rate:.1f}% tổng hồ sơ" if dxlth_rate > 0 else None,
            help="DXLTH_TOTAL: Số lượng hồ sơ xử lý đúng hạn"
        )

    with col3:
        dxlqh_rate = safe_number(summary.get('DXLQH', 0))
        delta_color = "inverse" if dxlqh_rate > 5 else "normal"
        st.metric(
            label="❌ Tỷ lệ xử lý quá hạn",
            value=f"{dxlqh_rate:.1f}%",
            delta=f"Vượt {dxlqh_rate:.1f}% giới hạn" if dxlqh_rate > 5 else f"Dưới giới hạn 5%",
            delta_color=delta_color,
            help="DXLQH: Tỷ lệ hồ sơ xử lý quá hạn (%)"
        )

    with col4:
        dxlqh_total = safe_int(summary.get('DXLQH_TOTAL', 0))
        st.metric(
            label="❌ Số lượng xử lý quá hạn",
            value=f"{dxlqh_total:,}".replace(',', '.'),
            delta=f"{dxlqh_rate:.1f}% tổng hồ sơ" if dxlqh_rate > 0 else None,
            delta_color="inverse" if dxlqh_total > 0 else "normal",
            help="DXLQH_TOTAL: Số lượng hồ sơ xử lý quá hạn"
        )

    st.divider()

    # ==============================================================================
    # 5. GIAO DỊCH THANH TOÁN TRỰC TUYẾN
    # ==============================================================================
    st.header("💳 GIAO DỊCH THANH TOÁN TRỰC TUYẾN")

    # Row 1: Tỷ lệ thanh toán
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        gdttdp_rate = safe_number(summary.get('GDTTDP', 0))
        st.metric(
            label="🏪 Tỷ lệ thanh toán điện tử địa phương",
            value=f"{gdttdp_rate:.1f}%",
            delta=None,
            help="GDTTDP: Tỷ lệ giao dịch thanh toán điện tử đối với dịch vụ công địa phương"
        )

    with col2:
        gdttqg_rate = safe_number(summary.get('GDTTQG', 0))
        st.metric(
            label="🌐 Tỷ lệ thanh toán qua DVCQG",
            value=f"{gdttqg_rate:.1f}%",
            delta=f"{gdttqg_rate - 50:.1f}% so với mục tiêu (50%)" if gdttqg_rate > 0 else None,
            help="GDTTQG: Tỷ lệ giao dịch thanh toán điện tử thông qua Cổng Dịch vụ công Quốc gia"
        )

    with col3:
        gdtt_total = safe_int(summary.get('GDTT_TOTAL', 0))
        st.metric(
            label="💰 Tổng hồ sơ có thanh toán điện tử",
            value=f"{gdtt_total:,}".replace(',', '.'),
            delta=None,
            help="GDTT_TOTAL: Tổng số hồ sơ có phát sinh giao dịch thanh toán điện tử (bao gồm cả địa phương và quốc gia)"
        )

    with col4:
        gdttqg_total = safe_int(summary.get('GDTTQG_TOTAL', 0))
        st.metric(
            label="🌐 Giao dịch thanh toán qua DVCQG",
            value=f"{gdttqg_total:,}".replace(',', '.'),
            delta=f"{gdttqg_rate:.1f}% tổng giao dịch" if gdttqg_rate > 0 else None,
            help="GDTTQG_TOTAL: Tổng số giao dịch thanh toán điện tử thực hiện qua Cổng Dịch vụ công Quốc gia"
        )

    # Row 2: TTHC trên DVCQG
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        nttqg_total = safe_int(summary.get('NTTQG_TOTAL', 0))
        st.metric(
            label="📋 TTHC cung cấp trên DVCQG",
            value=f"{nttqg_total:,}".replace(',', '.'),
            delta=None,
            help="NTTQG_TOTAL: Số lượng thủ tục hành chính được cung cấp trên Cổng Dịch vụ công Quốc gia"
        )

    st.divider()

    # ==============================================================================
    # 6. NHẬN VÀ XỬ LÝ KIẾN NGHỊ, PHẢN ÁNH
    # ==============================================================================
    st.header("📢 NHẬN VÀ XỬ LÝ KIẾN NGHỊ, PHẢN ÁNH")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        nttdxlth_rate = safe_number(summary.get('NTTDXLTH', 0))
        delta_color = "normal" if nttdxlth_rate >= 95 else "inverse"
        st.metric(
            label="✅ Tỷ lệ xử lý kiến nghị đúng hạn",
            value=f"{nttdxlth_rate:.1f}%",
            delta=f"{nttdxlth_rate - 95:.1f}% so với chuẩn (95%)",
            delta_color=delta_color,
            help="NTTDXLTH: Tỷ lệ kiến nghị, phản ánh xử lý đúng hạn"
        )

    with col2:
        nttdxlth_total = safe_int(summary.get('NTTDXLTH_TOTAL', 0))
        st.metric(
            label="✅ Số kiến nghị xử lý đúng hạn",
            value=f"{nttdxlth_total:,}".replace(',', '.'),
            delta=f"{nttdxlth_rate:.1f}% tổng kiến nghị" if nttdxlth_rate > 0 else None,
            help="NTTDXLTH_TOTAL: Số lượng kiến nghị, phản ánh xử lý đúng hạn"
        )

    with col3:
        nttdxlqh_rate = safe_number(summary.get('NTTDXLQH', 0))
        delta_color = "inverse" if nttdxlqh_rate > 5 else "normal"
        st.metric(
            label="❌ Tỷ lệ xử lý kiến nghị quá hạn",
            value=f"{nttdxlqh_rate:.1f}%",
            delta=f"Vượt {nttdxlqh_rate:.1f}% giới hạn" if nttdxlqh_rate > 5 else f"Dưới giới hạn 5%",
            delta_color=delta_color,
            help="NTTDXLQH: Tỷ lệ kiến nghị, phản ánh quá hạn xử lý"
        )

    with col4:
        nttdxlqh_total = safe_int(summary.get('NTTDXLQH_TOTAL', 0))
        st.metric(
            label="❌ Số kiến nghị xử lý quá hạn",
            value=f"{nttdxlqh_total:,}".replace(',', '.'),
            delta=f"{nttdxlqh_rate:.1f}% tổng kiến nghị" if nttdxlqh_rate > 0 else None,
            delta_color="inverse" if nttdxlqh_total > 0 else "normal",
            help="NTTDXLQH_TOTAL: Số lượng kiến nghị, phản ánh quá hạn xử lý"
        )

    st.divider()

    # ==============================================================================
    # 7. TỶ LỆ VÀ CÁC CHỈ SỐ KHÁC
    # ==============================================================================
    st.header("📊 TỶ LỆ VÀ CÁC CHỈ SỐ KHÁC")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tile_value = safe_number(summary.get('TILE', 0))
        delta_color = "normal" if tile_value >= 85 else "inverse"
        st.metric(
            label="🎯 Tỷ lệ đạt chỉ tiêu tổng",
            value=f"{tile_value:.1f}%",
            delta=f"{tile_value - 85:.1f}% so với chuẩn (85%)",
            delta_color=delta_color,
            help="TILE: Tỷ lệ tổng hồ sơ được xử lý đúng quy trình, đúng hạn"
        )

    with col2:
        tile_db_rate = safe_number(summary.get('TILE_DB', 0))
        delta_color = "normal" if tile_db_rate >= 95 else "inverse"
        st.metric(
            label="📋 Tỷ lệ TTHC công bố đúng hạn",
            value=f"{tile_db_rate:.1f}%",
            delta=f"{tile_db_rate - 95:.1f}% so với chuẩn (95%)",
            delta_color=delta_color,
            help="TILE_DB: Tỷ lệ thủ tục hành chính công bố đúng hạn"
        )

    st.divider()

    # ==============================================================================
    # 8. KHÔNG PHÁT SINH/CÁC CHỈ SỐ KHÁC
    # ==============================================================================
    st.header("📝 KHÔNG PHÁT SINH/CÁC CHỈ SỐ KHÁC")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tnktcs_total = safe_int(summary.get('TNKTCS_TOTAL', 0))
        st.metric(
            label="📝 Hồ sơ không phát sinh",
            value=f"{tnktcs_total:,}".replace(',', '.'),
            delta=None,
            help="TNKTCS_TOTAL: Tổng số hồ sơ (thủ tục) không phát sinh trong kỳ báo cáo"
        )
    

def _render_trend_chart(data):
    """Render biểu đồ xu hướng"""
    if not data['xuhuong']:
        st.info("Không có dữ liệu xu hướng điểm")
        return
        
    df_trend = pd.DataFrame(data['xuhuong'])
    df_trend['TB_SCORE'] = pd.to_numeric(df_trend['TB_SCORE'])
    df_trend['MONTH'] = pd.to_numeric(df_trend['MONTH'])
    df_trend = df_trend.sort_values('MONTH')
    
    fig = px.line(df_trend, 
                 x='MONTH', 
                 y='TB_SCORE',
                 title="📈 Xu hướng điểm số theo tháng",
                 markers=True,
                 line_shape='spline',
                 color_discrete_sequence=[CHART_COLORS['primary']])
    
    fig.update_layout(
        xaxis_title="Tháng",
        yaxis_title="Điểm số trung bình",
        hovermode='x unified'
    )
    
    # Thêm đường chuẩn
    fig.add_hline(y=70, line_dash="dash", line_color="red", 
                 annotation_text="Chuẩn tối thiểu (70 điểm)")
    fig.add_hline(y=85, line_dash="dash", line_color="green",
                 annotation_text="Chuẩn khá (85 điểm)")
    
    st.plotly_chart(fig, use_container_width=True)

def _render_gauge_chart(data):
    """Render biểu đồ gauge"""
    if not data['diem_tonghop']:
        st.info("Không có dữ liệu điểm tổng hợp")
        return
        
    current_score = float(data['diem_tonghop'][0]['TB_SCORE'])
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Điểm tổng hợp hiện tại"},
        delta = {'reference': 70},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': CHART_COLORS['primary']},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 70], 'color': "yellow"},
                {'range': [70, 85], 'color': "orange"},
                {'range': [85, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)

def _render_chi_so_766(data):
    """Render 7 nhóm chỉ số theo QĐ 766"""
    if not data['chiso']:
        st.info("Không có dữ liệu chỉ số")
        return
        
    st.subheader("📊 7 Nhóm chỉ số theo Quyết định 766/QĐ-TTg")
    
    df_chiso = pd.DataFrame(data['chiso'])
    df_chiso['TB_SCORE'] = pd.to_numeric(df_chiso['TB_SCORE'])
    df_chiso['MAX_SCORE'] = pd.to_numeric(df_chiso['MAX_SCORE'])
    df_chiso['SCORE'] = pd.to_numeric(df_chiso['SCORE'])
    
    # Tạo biểu đồ radar
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=df_chiso['TB_SCORE'].tolist(),
        theta=df_chiso['DESCRIPTION'].tolist(),
        fill='toself',
        name='Điểm hiện tại',
        line_color=CHART_COLORS['primary']
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[100] * len(df_chiso),
        theta=df_chiso['DESCRIPTION'].tolist(),
        fill='toself',
        name='Điểm tối đa (100%)',
        line_color=CHART_COLORS['danger'],
        opacity=0.3
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title="Biểu đồ radar 7 nhóm chỉ số"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Bảng chi tiết
    st.subheader("📋 Chi tiết 7 nhóm chỉ số")
    df_display = df_chiso[['CODE', 'DESCRIPTION', 'SCORE', 'MAX_SCORE', 'TB_SCORE']].copy()
    df_display.columns = ['Mã', 'Tên chỉ số', 'Điểm đạt', 'Điểm tối đa', 'Tỷ lệ %']
    df_display['Tỷ lệ %'] = df_display['Tỷ lệ %'].round(2)
    
    st.dataframe(df_display, use_container_width=True)
