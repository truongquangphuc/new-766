import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.config import CHART_COLORS
from typing import Dict, List, Optional, Any, Union


class TinhViewRenderer:
    """Class để quản lý việc hiển thị view cấp tỉnh"""
    
    def __init__(self, data: Dict[str, Any], tinh_name: str):
        self.data = data
        self.tinh_name = tinh_name
        self.summary = None
    
    def render(self):
        """Entry point chính để render view"""
        # Hiển thị dữ liệu report_766 nếu có
        if self.data.get('report_tinh_766_service') and len(self.data['report_tinh_766_service']) > 0:
            filtered = [item for item in self.data['report_tinh_766_service'] if item.get("ID") == "398126"]
            if filtered:
                record = filtered[0]
                tong_diem = record.get("TONG_SCORE", "N/A")
                xep_hang = record.get("ROW_STT", "N/A")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(
                        f"""
                        <div style="text-align:center;">
                        <div style="font-size:17px; color: #888; font-weight: 400; letter-spacing:1px; margin-bottom: 5px;">
                            Tổng điểm
                        </div>
                        <div style="font-size:52px; font-weight: bold; line-height: 1; color: #1c1c1c; display: flex; justify-content: center; align-items: center; gap:13px;">
                            <span style="font-size:36px; vertical-align:middle;">⭐️</span>
                            <span>{tong_diem}</span>
                        </div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                with col2:
                    st.markdown(
                        f"""
                        <div style="text-align:center;">
                        <div style="font-size:17px; color: #888; font-weight: 400; letter-spacing:1px; margin-bottom: 5px;">
                            Xếp hạng
                        </div>
                        <div style="font-size:52px; font-weight: bold; line-height: 1; color: #1c1c1c; display: flex; justify-content: center; align-items: center; gap:13px;">
                            <span style="font-size:36px; vertical-align:middle;">🏆</span>
                            <span>{xep_hang}</span>
                        </div>
                        </div>
                        """, unsafe_allow_html=True
                    )
            else:
                st.info("Không tìm thấy bản ghi có ID = 398126")
        else:
            st.info("Không có dữ liệu báo cáo 766 để hiển thị")
        st.divider()

        self._render_charts()
        self._render_chi_so_766()
        # st.divider()
        # self._render_overview_metrics()
    
    def _render_charts(self):
        """Render biểu đồ xu hướng và gauge"""
        col1, col2 = st.columns([2, 1])
        with col1:
            TinhChartRenderer.render_trend_chart(self.data)
        with col2:
            TinhChartRenderer.render_gauge_chart(self.data)
    
    def _render_chi_so_766(self):
        """Render 7 nhóm chỉ số theo QĐ 766"""
        TinhChartRenderer.render_chi_so_766(self.data)
    
    def _render_overview_metrics(self):
        """Render metrics tổng quan"""
        if not self._validate_summary_data():
            return
        
        self.summary = self.data['monthly_summary'][0]
        metrics_renderer = TinhMetricsRenderer(self.summary)
        metrics_renderer.render_all_metrics()
    
    def _validate_summary_data(self) -> bool:
        """Kiểm tra dữ liệu summary"""
        if not self.data.get('monthly_summary'):
            st.warning("Không có dữ liệu tổng hợp")
            return False
        return True


class TinhChartRenderer:
    """Class chuyên xử lý việc render biểu đồ cho tỉnh"""
    
    @staticmethod
    def render_trend_chart(data: Dict[str, Any]):
        """Render biểu đồ xu hướng"""
        if not data.get('xuhuong'):
            st.info("Không có dữ liệu xu hướng điểm")
            return
        
        df_trend = pd.DataFrame(data['xuhuong'])
        df_trend = TinhChartRenderer._prepare_trend_data(df_trend)
        
        fig = px.line(
            df_trend, 
            x='MONTH', 
            y='TB_SCORE',
            title="📈 Xu hướng điểm số theo tháng",
            markers=True,
            line_shape='spline',
            color_discrete_sequence=[CHART_COLORS['primary']]
        )
        
        TinhChartRenderer._update_trend_layout(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _prepare_trend_data(df: pd.DataFrame) -> pd.DataFrame:
        """Chuẩn bị dữ liệu trend"""
        df['TB_SCORE'] = pd.to_numeric(df['TB_SCORE'])
        df['MONTH'] = pd.to_numeric(df['MONTH'])
        return df.sort_values('MONTH')
    
    @staticmethod
    def _update_trend_layout(fig):
        """Cập nhật layout cho trend chart"""
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
    
    @staticmethod
    def render_gauge_chart(data: Dict[str, Any]):
        """Render biểu đồ gauge"""
        if not data.get('diem_tonghop'):
            st.info("Không có dữ liệu điểm tổng hợp")
            return
        
        current_score = float(data['diem_tonghop'][0]['TB_SCORE'])
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Điểm cả năm"},
            delta={'reference': 70},
            gauge=TinhChartRenderer._get_gauge_config()
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _get_gauge_config() -> Dict:
        """Cấu hình cho gauge chart"""
        return {
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
    
    @staticmethod
    def render_chi_so_766(data: Dict[str, Any]):
        """Render 7 nhóm chỉ số theo QĐ 766"""
        if not data.get('chiso'):
            st.info("Không có dữ liệu chỉ số")
            return
        
        st.subheader("📊 7 Nhóm chỉ số theo Quyết định 766/QĐ-TTg")
        
        df_chiso = TinhChartRenderer._prepare_chiso_data(data['chiso'])
        
        # Tạo biểu đồ radar
        fig = TinhChartRenderer._create_radar_chart(df_chiso)
        st.plotly_chart(fig, use_container_width=True)
        
        # Bảng chi tiết
        TinhChartRenderer._render_chiso_table(df_chiso)
    
    @staticmethod
    def _prepare_chiso_data(chiso_data: List[Dict]) -> pd.DataFrame:
        """Chuẩn bị dữ liệu chỉ số"""
        df = pd.DataFrame(chiso_data)
        numeric_columns = ['TB_SCORE', 'MAX_SCORE', 'SCORE']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col])
        return df
    
    @staticmethod
    def _create_radar_chart(df: pd.DataFrame) -> go.Figure:
        """Tạo biểu đồ radar"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=df['TB_SCORE'].tolist(),
            theta=df['DESCRIPTION'].tolist(),
            fill='toself',
            name='Điểm hiện tại',
            line_color=CHART_COLORS['primary']
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=[100] * len(df),
            theta=df['DESCRIPTION'].tolist(),
            fill='toself',
            name='Điểm tối đa (100%)',
            line_color=CHART_COLORS.get('danger', 'red'),
            opacity=0.3
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Biểu đồ radar 7 nhóm chỉ số"
        )
        
        return fig
    
    @staticmethod
    def _render_chiso_table(df: pd.DataFrame):
        """Render bảng chi tiết chỉ số"""
        st.subheader("📋 Chi tiết 7 nhóm chỉ số")
        df_display = df[['CODE', 'DESCRIPTION', 'SCORE', 'MAX_SCORE', 'TB_SCORE']].copy()
        df_display.columns = ['Mã', 'Tên chỉ số', 'Điểm đạt', 'Điểm tối đa', 'Tỷ lệ %']
        df_display['Tỷ lệ %'] = df_display['Tỷ lệ %'].round(2)
        st.dataframe(df_display, use_container_width=True)


class TinhMetricsRenderer:
    """Class chuyên xử lý việc render metrics cho tỉnh"""
    
    def __init__(self, summary: Dict[str, Any]):
        self.summary = summary
    
    def render_all_metrics(self):
        """Render tất cả các nhóm metrics"""
        metrics_groups = [
            ('📊 TỔNG HỢP HỒ SƒO, KẾT QUẢ XỬ LÝ', self._render_tong_hop_metrics),
            ('📝 HÌNH THỨC NỘP HỒ SƒO THỦ TỤC HÀNH CHÍNH', self._render_hinh_thuc_nop_metrics),
            ('📤 HÌNH THỨC TRẢ KẾT QUẢ THỦ TỤC HÀNH CHÍNH', self._render_hinh_thuc_tra_metrics),
            ('⚡ KẾT QUẢ XỬ LÝ', self._render_ket_qua_xl_metrics),
            ('💳 GIAO DỊCH THANH TOÁN TRỰC TUYẾN', self._render_thanh_toan_metrics),
            ('📢 NHẬN VÀ XỬ LÝ KIẾN NGHỊ, PHẢN ÁNH', self._render_kien_nghi_metrics),
            ('📊 TỶ LỆ VÀ CÁC CHỈ SỐ KHÁC', self._render_ty_le_khac_metrics),
            ('📝 KHÔNG PHÁT SINH/CÁC CHỈ SỐ KHÁC', self._render_khong_phat_sinh_metrics)
        ]
        
        for title, render_func in metrics_groups:
            st.header(title)
            render_func()
            st.divider()
    
    def _render_tong_hop_metrics(self):
        """Render metrics tổng hợp hồ sơ"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            hs_total = safe_int(self.summary.get('HS_TOTAL', 0))
            self._render_metric(
                "📋 Tổng số hồ sơ TTHC tiếp nhận, giải quyết",
                f"{hs_total:,}".replace(',', '.'),
                None,
                "HS_TOTAL: Tổng số hồ sơ thủ tục hành chính (TTHC) tiếp nhận, giải quyết"
            )
        
        with col2:
            db_total = safe_int(self.summary.get('DB_TOTAL', 0))
            db_rate = (db_total / hs_total * 100) if hs_total > 0 else 0
            self._render_metric(
                "☁️ Tổng số hồ sơ đồng bộ lên DVCQG",
                f"{db_total:,}".replace(',', '.'),
                f"Tỷ lệ: {db_rate:.1f}%",
                "DB_TOTAL: Tổng số hồ sơ đã đồng bộ lên Cổng Dịch vụ công Quốc gia"
            )
        
        with col3:
            tntk_total = safe_int(self.summary.get('TNTK_TOTAL', 0))
            self._render_metric(
                "📈 Số TTHC được tính toán thống kê",
                f"{tntk_total:,}".replace(',', '.'),
                None,
                "TNTK_TOTAL: Tổng số thủ tục hành chính được tính toán thống kê trong kỳ báo cáo"
            )
    
    def _render_hinh_thuc_nop_metrics(self):
        """Render metrics hình thức nộp"""
        # Row 1: Nộp trực tiếp và bưu chính
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            tructiep_rate = safe_number(self.summary.get('HTN_TRUCTIEP', 0))
            self._render_metric(
                "🏢 Tỷ lệ nộp trực tiếp",
                f"{tructiep_rate:.1f}%",
                None,
                "HTN_TRUCTIEP: Tỷ lệ hồ sơ nộp trực tiếp tại bộ phận tiếp nhận"
            )
        
        with col2:
            tructiep_total = safe_int(self.summary.get('HTN_TRUCTIEP_TOTAL', 0))
            self._render_metric(
                "🏢 Số lượng nộp trực tiếp",
                f"{tructiep_total:,}".replace(',', '.'),
                f"{tructiep_rate:.1f}% tổng hồ sơ" if tructiep_rate > 0 else None,
                "HTN_TRUCTIEP_TOTAL: Số lượng hồ sơ nộp trực tiếp"
            )
        
        with col3:
            buuchinh_rate = safe_number(self.summary.get('HTN_BUUCHINH', 0))
            self._render_metric(
                "📮 Tỷ lệ nộp qua bưu chính",
                f"{buuchinh_rate:.1f}%",
                None,
                "HTN_BUUCHINH: Tỷ lệ hồ sơ nộp qua bưu chính"
            )
        
        with col4:
            buuchinh_total = safe_int(self.summary.get('HTN_BUUCHINH_TOTAL', 0))
            self._render_metric(
                "📮 Số lượng nộp qua bưu chính",
                f"{buuchinh_total:,}".replace(',', '.'),
                f"{buuchinh_rate:.1f}% tổng hồ sơ" if buuchinh_rate > 0 else None,
                "HTN_BUUCHINH_TOTAL: Số lượng hồ sơ nộp qua bưu chính"
            )
        
        # Row 2: Nộp trực tuyến
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            tructuyen_rate = safe_number(self.summary.get('HTN_TRUCTUYEN', 0))
            delta_color = "normal" if tructuyen_rate >= 70 else "inverse"
            self._render_metric(
                "💻 Tỷ lệ nộp trực tuyến chuẩn",
                f"{tructuyen_rate:.1f}%",
                f"{tructuyen_rate - 70:.1f}% so với chuẩn (70%)",
                "HTN_TRUCTUYEN: Tỷ lệ hồ sơ nộp trực tuyến (online)",
                delta_color
            )
        
        with col2:
            tructuyen_total = safe_int(self.summary.get('HTN_TRUCTUYEN_TOTAL', 0))
            self._render_metric(
                "💻 Số lượng nộp trực tuyến chuẩn",
                f"{tructuyen_total:,}".replace(',', '.'),
                f"{tructuyen_rate:.1f}% tổng hồ sơ" if tructuyen_rate > 0 else None,
                "HTN_TRUCTUYEN_TOTAL: Số lượng hồ sơ nộp trực tuyến chuẩn"
            )
        
        with col3:
            tructuyen_kc_rate = safe_number(self.summary.get('HTN_TRUCTUYEN_KHONGCHUAN', 0))
            delta_color = "inverse" if tructuyen_kc_rate > 10 else "normal"
            self._render_metric(
                "📧 Tỷ lệ trực tuyến không chuẩn",
                f"{tructuyen_kc_rate:.1f}%",
                None,
                "HTN_TRUCTUYEN_KHONGCHUAN: Tỷ lệ hồ sơ nộp trực tuyến chưa chuẩn hóa",
                delta_color
            )
        
        with col4:
            tructuyen_kc_total = safe_int(self.summary.get('HTN_TRUCTUYEN_KHONGCHUAN_TOTAL', 0))
            self._render_metric(
                "📧 Số lượng trực tuyến không chuẩn",
                f"{tructuyen_kc_total:,}".replace(',', '.'),
                f"{tructuyen_kc_rate:.1f}% tổng hồ sơ" if tructuyen_kc_rate > 0 else None,
                "HTN_TRUCTUYEN_KHONGCHUAN_TOTAL: Số lượng hồ sơ nộp trực tuyến không chuẩn"
            )
    
    def _render_hinh_thuc_tra_metrics(self):
        """Render metrics hình thức trả kết quả"""
        col1, col2, col3, col4 = st.columns(4)
        
        metrics_config = [
            ("✅ Tỷ lệ trả kết quả đúng hạn", 'HTDH', 90, "HTDH: Tỷ lệ hồ sơ trả kết quả đúng hạn"),
            ("✅ Số lượng trả kết quả đúng hạn", 'HTDH_TOTAL', None, "HTDH_TOTAL: Số lượng hồ sơ trả kết quả đúng hạn"),
            ("❌ Tỷ lệ trả kết quả quá hạn", 'HTQH', 10, "HTQH: Tỷ lệ hồ sơ trả kết quả quá hạn"),
            ("❌ Số lượng trả kết quả quá hạn", 'HTQH_TOTAL', None, "HTQH_TOTAL: Số lượng hồ sơ trả kết quả quá hạn")
        ]
        
        columns = [col1, col2, col3, col4]
        for i, (label, key, benchmark, help_text) in enumerate(metrics_config):
            with columns[i]:
                self._render_benchmark_metric(label, key, benchmark, help_text)
    
    def _render_ket_qua_xl_metrics(self):
        """Render metrics kết quả xử lý"""
        col1, col2, col3, col4 = st.columns(4)
        
        metrics_config = [
            ("✅ Tỷ lệ xử lý đúng hạn", 'DXLTH', 95, "DXLTH: Tỷ lệ hồ sơ xử lý đúng hạn (%)"),
            ("✅ Số lượng xử lý đúng hạn", 'DXLTH_TOTAL', None, "DXLTH_TOTAL: Số lượng hồ sơ xử lý đúng hạn"),
            ("❌ Tỷ lệ xử lý quá hạn", 'DXLQH', 5, "DXLQH: Tỷ lệ hồ sơ xử lý quá hạn (%)"),
            ("❌ Số lượng xử lý quá hạn", 'DXLQH_TOTAL', None, "DXLQH_TOTAL: Số lượng hồ sơ xử lý quá hạn")
        ]
        
        columns = [col1, col2, col3, col4]
        for i, (label, key, benchmark, help_text) in enumerate(metrics_config):
            with columns[i]:
                self._render_benchmark_metric(label, key, benchmark, help_text)
    
    def _render_thanh_toan_metrics(self):
        """Render metrics thanh toán trực tuyến"""
        # Row 1: Tỷ lệ thanh toán
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            gdttdp_rate = safe_number(self.summary.get('GDTTDP', 0))
            self._render_metric(
                "🏪 Tỷ lệ thanh toán điện tử địa phương",
                f"{gdttdp_rate:.1f}%",
                None,
                "GDTTDP: Tỷ lệ giao dịch thanh toán điện tử đối với dịch vụ công địa phương"
            )
        
        with col2:
            gdttqg_rate = safe_number(self.summary.get('GDTTQG', 0))
            self._render_metric(
                "🌐 Tỷ lệ thanh toán qua DVCQG",
                f"{gdttqg_rate:.1f}%",
                f"{gdttqg_rate - 50:.1f}% so với mục tiêu (50%)" if gdttqg_rate > 0 else None,
                "GDTTQG: Tỷ lệ giao dịch thanh toán điện tử thông qua Cổng Dịch vụ công Quốc gia"
            )
        
        with col3:
            gdtt_total = safe_int(self.summary.get('GDTT_TOTAL', 0))
            self._render_metric(
                "💰 Tổng hồ sơ có thanh toán điện tử",
                f"{gdtt_total:,}".replace(',', '.'),
                None,
                "GDTT_TOTAL: Tổng số hồ sơ có phát sinh giao dịch thanh toán điện tử"
            )
        
        with col4:
            gdttqg_total = safe_int(self.summary.get('GDTTQG_TOTAL', 0))
            self._render_metric(
                "🌐 Giao dịch thanh toán qua DVCQG",
                f"{gdttqg_total:,}".replace(',', '.'),
                f"{gdttqg_rate:.1f}% tổng giao dịch" if gdttqg_rate > 0 else None,
                "GDTTQG_TOTAL: Tổng số giao dịch thanh toán điện tử thực hiện qua DVCQG"
            )
        
        # Row 2: TTHC trên DVCQG
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            nttqg_total = safe_int(self.summary.get('NTTQG_TOTAL', 0))
            self._render_metric(
                "📋 TTHC cung cấp trên DVCQG",
                f"{nttqg_total:,}".replace(',', '.'),
                None,
                "NTTQG_TOTAL: Số lượng thủ tục hành chính được cung cấp trên DVCQG"
            )
    
    def _render_kien_nghi_metrics(self):
        """Render metrics kiến nghị, phản ánh"""
        col1, col2, col3, col4 = st.columns(4)
        
        metrics_config = [
            ("✅ Tỷ lệ xử lý kiến nghị đúng hạn", 'NTTDXLTH', 95, "NTTDXLTH: Tỷ lệ kiến nghị, phản ánh xử lý đúng hạn"),
            ("✅ Số kiến nghị xử lý đúng hạn", 'NTTDXLTH_TOTAL', None, "NTTDXLTH_TOTAL: Số lượng kiến nghị, phản ánh xử lý đúng hạn"),
            ("❌ Tỷ lệ xử lý kiến nghị quá hạn", 'NTTDXLQH', 5, "NTTDXLQH: Tỷ lệ kiến nghị, phản ánh quá hạn xử lý"),
            ("❌ Số kiến nghị xử lý quá hạn", 'NTTDXLQH_TOTAL', None, "NTTDXLQH_TOTAL: Số lượng kiến nghị, phản ánh quá hạn xử lý")
        ]
        
        columns = [col1, col2, col3, col4]
        for i, (label, key, benchmark, help_text) in enumerate(metrics_config):
            with columns[i]:
                self._render_benchmark_metric(label, key, benchmark, help_text)
    
    def _render_ty_le_khac_metrics(self):
        """Render tỷ lệ và các chỉ số khác"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            tile_value = safe_number(self.summary.get('TILE', 0))
            delta_color = "normal" if tile_value >= 85 else "inverse"
            self._render_metric(
                "🎯 Tỷ lệ đạt chỉ tiêu tổng",
                f"{tile_value:.1f}%",
                f"{tile_value - 85:.1f}% so với chuẩn (85%)",
                "TILE: Tỷ lệ tổng hồ sơ được xử lý đúng quy trình, đúng hạn",
                delta_color
            )
        
        with col2:
            tile_db_rate = safe_number(self.summary.get('TILE_DB', 0))
            delta_color = "normal" if tile_db_rate >= 95 else "inverse"
            self._render_metric(
                "📋 Tỷ lệ TTHC công bố đúng hạn",
                f"{tile_db_rate:.1f}%",
                f"{tile_db_rate - 95:.1f}% so với chuẩn (95%)",
                "TILE_DB: Tỷ lệ thủ tục hành chính công bố đúng hạn",
                delta_color
            )
    
    def _render_khong_phat_sinh_metrics(self):
        """Render metrics không phát sinh"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            tnktcs_total = safe_int(self.summary.get('TNKTCS_TOTAL', 0))
            self._render_metric(
                "📝 Hồ sơ không phát sinh",
                f"{tnktcs_total:,}".replace(',', '.'),
                None,
                "TNKTCS_TOTAL: Tổng số hồ sơ (thủ tục) không phát sinh trong kỳ báo cáo"
            )
    
    def _render_benchmark_metric(self, label: str, key: str, benchmark: Optional[float], help_text: str):
        """Render metric với benchmark"""
        if key.endswith('_TOTAL'):
            value = safe_int(self.summary.get(key, 0))
            formatted_value = f"{value:,}".replace(',', '.')
            rate_key = key.replace('_TOTAL', '')
            rate = safe_number(self.summary.get(rate_key, 0))
            delta = f"{rate:.1f}% tổng" if rate > 0 else None
            delta_color = "inverse" if "quá hạn" in label and value > 0 else "normal"
        else:
            rate = safe_number(self.summary.get(key, 0))
            formatted_value = f"{rate:.1f}%"
            if benchmark:
                if "quá hạn" in label:
                    delta = f"Vượt {rate:.1f}% giới hạn" if rate > benchmark else f"Dưới giới hạn {benchmark}%"
                    delta_color = "inverse" if rate > benchmark else "normal"
                else:
                    delta = f"{rate - benchmark:.1f}% so với chuẩn ({benchmark}%)"
                    delta_color = "normal" if rate >= benchmark else "inverse"
            else:
                delta = None
                delta_color = "normal"
        
        self._render_metric(label, formatted_value, delta, help_text, delta_color)
    
    def _render_metric(self, label: str, value: str, delta: Optional[str], 
                      help_text: str, delta_color: str = "normal"):
        """Render một metric"""
        st.metric(
            label=label,
            value=value,
            delta=delta,
            delta_color=delta_color,
            help=help_text
        )


# Utility functions
def safe_number(value: Union[str, int, float, None], default: float = 0) -> float:
    """Chuyển đổi giá trị về số, trả về default nếu không thể chuyển đổi"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_int(value: Union[str, int, float, None], default: int = 0) -> int:
    """Chuyển đổi giá trị về số nguyên, trả về default nếu không thể chuyển đổi"""
    try:
        return int(float(value)) if value is not None else default
    except (ValueError, TypeError):
        return default


# Entry point function - tương thích với code cũ
def render_tinh_view(data: Dict[str, Any], tinh_name: str):
    """Entry point chính - tương thích với code cũ"""
    renderer = TinhViewRenderer(data, tinh_name)
    renderer.render()
