import streamlit as st
import pandas as pd
import plotly.express as px
from utils.config import CHART_COLORS
from typing import Dict, List, Any
from get_tthc_chitiet import APIClient

class SoBanViewRenderer:
    """Class để quản lý việc hiển thị view của Sở/Ban"""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.selected_tthc_id = None
        self.selected_tthc_name = None

    def render(self):
        """Entry point chính để render view"""
        if not self._validate_data():
            return
        if not self._render_selector():
            return
        self._render_766_chart()
        # self._render_reports()

    def _validate_data(self) -> bool:
        """Kiểm tra và validate dữ liệu đầu vào"""
        if not self.data.get('766_report_filtered_so_nganh'):
            st.info("Không có dữ liệu TTHC chi tiết")
            return False
        return True

    def _render_selector(self) -> bool:
        """Render selectbox và lưu thông tin được chọn"""
        tthc_data = self.data.get('766_report_filtered_so_nganh', [])
        if not tthc_data:
            st.warning("⚠️ Không có dữ liệu Sở/Ban để hiển thị")
            return False

        # Mapping giữa tên hiển thị và dữ liệu
        options_mapping = {
            f"{item['TEN']} (MA_COQUAN: {item['MA_COQUAN']})": item
            for item in tthc_data
        }

        # Danh sách options
        options_list = list(options_mapping.keys())

        # Selectbox
        selected_option = st.selectbox(
            "🏢 Chọn Sở/Ban để xem báo cáo:",
            options=options_list,
            index=0,
            help="Chọn đơn vị để xem báo cáo chi tiết 766",
            key="so_ban_selector"
        )

        # Lấy dữ liệu item đã chọn
        selected_tthc = options_mapping[selected_option]
        self.selected_tthc_id = selected_tthc['MA_COQUAN']
        self.selected_tthc_name = selected_tthc['TEN']

        # --- Hiển thị thêm ---
        # Vị trí (index) trong danh sách
        selected_index = options_list.index(selected_option) + 1  # +1 để đếm từ 1 thay vì 0

        # In ra thông tin dưới selectbox
        st.markdown(
            f"""
            <div style="font-size:24px; font-weight:bold; color:#1f77b4;">
                📊 TỔNG ĐIỂM: {selected_tthc['TONG_SCORE']} &nbsp;&nbsp;|&nbsp;&nbsp; 🔢 XẾP HẠNG: {selected_index} / {len(options_list)}
            </div>
            """,
            unsafe_allow_html=True
        )


        return True

    def _render_766_chart(self):
        """Render biểu đồ chỉ số 766"""
        st.subheader(f"{self.selected_tthc_name}", divider='rainbow')

        if not self.data.get('report_766'):
            st.warning("⚠️ Không có dữ liệu report_766")
            return

        item = next(
            (item for item in self.data['report_766']
             if item['MA_COQUAN'] == self.selected_tthc_id),
            None
        )

        if not item:
            st.error(f"Không tìm thấy dữ liệu chỉ số 766 cho {self.selected_tthc_name}")
            return

        target = self._build_target_data(item)
        standard = self._get_standard_scores()
        ChartRenderer.plot_766_barchart(
            self.selected_tthc_name.split(' - ')[0], target, standard
        )

    def _build_target_data(self, item: Dict) -> Dict[str, float]:
        field_mapping = {
            "Công khai, minh bạch": 'CKMB',
            "Tiến độ giải quyết": 'TDGQ',
            "Dịch vụ công trực tuyến": 'CLGQ',
            "Thanh toán trực tuyến": 'TTTT',
            "Mức độ hài lòng": 'MDHL',
            "Số hóa hồ sơ": 'MDSH',
            "Điểm tổng": 'TONG_SCORE',
        }
        return {
            key: float(item.get(field, 0))
            for key, field in field_mapping.items()
        }

    @staticmethod
    def _get_standard_scores() -> Dict[str, int]:
        return {
            "Công khai, minh bạch": 18,
            "Tiến độ giải quyết": 20,
            "Dịch vụ công trực tuyến": 12,
            "Thanh toán trực tuyến": 10,
            "Mức độ hài lòng": 18,
            "Số hóa hồ sơ": 22,
        }

    def _render_reports(self):
        reporters = [
            SoBanChiTietReporter(self.data, 'report_chitiet'),
            SoBanOnlineReporter(self.data, 'report_chitiet_online'),
            SoBanDigitizationReporter(self.data, 'report_digitization'),
        ]
        for reporter in reporters:
            reporter.render(self.selected_tthc_id, self.selected_tthc_name)

class BaseSoBanReporter:
    """Base class cho các reporter của Sở/Ban"""
    def __init__(self, data: Dict, data_key: str):
        self.data = data
        self.data_key = data_key

    def render(self, selected_id: str, selected_name: str):
        if not self._validate_data():
            return
        filtered_data = self._get_filtered_data(selected_id, selected_name)
        if not filtered_data:
            self._show_fallback_data()
            filtered_data = self.data[self.data_key]
        self._render_content(filtered_data)

    def _validate_data(self) -> bool:
        if self.data_key not in self.data or not self.data[self.data_key]:
            self._show_no_data_warning()
            return False
        return True

    def _show_no_data_warning(self):
        st.warning(f"⚠️ Không có dữ liệu {self.data_key}")

    def _get_filtered_data(self, selected_id: str, selected_name: str) -> List[Dict]:
        raise NotImplementedError

    def _show_fallback_data(self):
        total_records = len(self.data[self.data_key])
        st.warning(f"⚠️ Không tìm thấy dữ liệu phù hợp")
        st.info(f"💡 Hiển thị tất cả {total_records} bản ghi thay thế")

    def _render_content(self, filtered_data: List[Dict]):
        raise NotImplementedError

class SoBanChiTietReporter(BaseSoBanReporter):
    """Reporter cho báo cáo chi tiết KGG của Sở/Ban"""
    def _get_filtered_data(self, selected_id: str, selected_name: str) -> List[Dict]:
        return [
            item for item in self.data[self.data_key]
            if item.get('agency', {}).get('code') == selected_id
        ]

    def _show_fallback_data(self):
        total_records = len(self.data[self.data_key])
        st.warning(f"⚠️ Không tìm thấy dữ liệu với CODE")
        st.info(f"💡 Hiển thị tất cả {total_records} bản ghi thay thế")

    def _render_content(self, filtered_data: List[Dict]):
        st.subheader("📋 Kết quả xử lý hồ sơ trên một cửa điện tử", divider='blue')
        SoBanTableRenderer.render_chitiet_table(filtered_data)

class SoBanOnlineReporter(BaseSoBanReporter):
    """Reporter cho báo cáo chi tiết online của Sở/Ban"""
    def _show_no_data_warning(self):
        st.warning("⚠️ Không có dữ liệu báo cáo chi tiết các TTHC online")

    def _get_filtered_data(self, selected_id: str, selected_name: str) -> List[Dict]:
        clean_name = selected_name.replace(" - tỉnh An Giang", "").strip().lower()
        return [
            item for item in self.data[self.data_key]
            if self._name_matches(item.get('agency_name', '').lower(), clean_name)
        ]

    @staticmethod
    def _name_matches(agency_name: str, target_name: str) -> bool:
        return (agency_name == target_name or
                target_name in agency_name)

    def _show_fallback_data(self):
        total_records = len(self.data[self.data_key])
        st.warning(f"⚠️ Không tìm thấy dữ liệu với TÊN")
        st.info(f"💡 Hiển thị tất cả {total_records} bản ghi thay thế")

    def _render_content(self, filtered_data: List[Dict]):
        SoBanTableRenderer.render_online_table(filtered_data)

class SoBanDigitizationReporter(BaseSoBanReporter):
    """Reporter cho báo cáo số hóa của Sở/Ban"""
    def _show_no_data_warning(self):
        st.warning("⚠️ Không có dữ liệu báo cáo chi tiết")

    def _get_filtered_data(self, selected_id: str, selected_name: str) -> List[Dict]:
        return [
            item for item in self.data[self.data_key]
            if item.get('agency', {}).get('code') == selected_id
        ]

    def _show_fallback_data(self):
        total_records = len(self.data[self.data_key])
        st.warning(f"⚠️ Không tìm thấy dữ liệu với CODE")
        st.info(f"💡 Hiển thị tất cả {total_records} bản ghi thay thế")

    def _render_content(self, filtered_data: List[Dict]):
        SoBanTableRenderer.render_digitization_table(filtered_data)

class SoBanTableRenderer:
    """Class chuyên xử lý việc render các bảng cho Sở/Ban"""
    @staticmethod
    def render_chitiet_table(data: List[Dict]):
        if not data:
            st.info("Không có dữ liệu để hiển thị")
            return
        columns = {
            'Tên cơ quan': lambda item: item.get('agency', {}).get('name', 'N/A'),
            'Đã nhận': lambda item: SoBanTableRenderer._format_number(item.get('received', 0)),
            'Đã giải quyết': lambda item: SoBanTableRenderer._format_number(item.get('resolved', 0)),
            'Trực tuyến': lambda item: SoBanTableRenderer._format_number(item.get('receivedOnline', 0)),
            'Trực tiếp': lambda item: SoBanTableRenderer._format_number(item.get('receivedDirect', 0)),
            'Quá hạn': lambda item: SoBanTableRenderer._format_number(item.get('resolvedOverdue', 0)),
        }
        df = SoBanTableRenderer._build_dataframe(data, columns)
        st.markdown('#### 🟢 Thống kê tổng hợp xử lý hồ sơ')
        st.dataframe(df, use_container_width=True, hide_index=True)

    @staticmethod
    def render_online_table(data: List[Dict]):
        if not data:
            st.info("Không có dữ liệu để hiển thị")
            return
        columns = {
            'Tên cơ quan': lambda item: item.get('agency_name', 'N/A'),
            'Phát sinh 1 phần': lambda item: SoBanTableRenderer._format_number(item.get('phatsinh_1phan_quantity', 0)),
            'Phát sinh toàn phần': lambda item: SoBanTableRenderer._format_number(item.get('phatsinh_toanphan_quantity', 0)),
            'Chờ tiếp nhận': lambda item: SoBanTableRenderer._format_number(item.get('chotiepnhan_quantity', 0)),
            'Đã tiếp nhận': lambda item: SoBanTableRenderer._format_number(item.get('datiepnhan_quantity', 0)),
            'Hoàn thành': lambda item: SoBanTableRenderer._format_number(item.get('hoanthanh_quantity', 0)),
            'Từ chối': lambda item: SoBanTableRenderer._format_number(item.get('tuchoi_quantity', 0)),
            'Thanh toán online': lambda item: SoBanTableRenderer._format_number(item.get('onlinepaid_quantity', 0)),
            'Tổng cộng': lambda item: f"{item.get('total', 0):,.1f}".replace(',', '.'),
        }
        df = SoBanTableRenderer._build_dataframe(data, columns)
        st.markdown('#### 🟠 Thống kê số liệu về hồ sơ trực tuyến')
        st.dataframe(df, use_container_width=True, hide_index=True)

    @staticmethod
    def render_digitization_table(data: List[Dict]):
        if not data:
            st.info("Không có dữ liệu để hiển thị")
            return
        columns = {
            'Tên cơ quan': lambda item: item.get('agency', {}).get('name', 'N/A'),
            'Tổng tiếp nhận': lambda item: SoBanTableRenderer._format_number(item.get('totalReceiver', 0)),
            'Tiếp nhận có file': lambda item: SoBanTableRenderer._format_number(item.get('totalReceiverHavingFile', 0)),
            'Tổng hoàn thành': lambda item: SoBanTableRenderer._format_number(item.get('totalComplete', 0)),
            'Hoàn thành có file': lambda item: SoBanTableRenderer._format_number(item.get('totalCompleteHavingFile', 0)),
            'Tiếp nhận không file': lambda item: SoBanTableRenderer._format_number(item.get('totalReceiverNopeFile', 0)),
            'Hoàn thành không file': lambda item: SoBanTableRenderer._format_number(item.get('totalCompleteNopeFile', 0)),
            'Tiếp nhận & hoàn thành có file': lambda item: SoBanTableRenderer._format_number(item.get('totalReceiverCompleteHavingFile', 0)),
            '% Tiếp nhận có file': lambda item: f"{item.get('percentTotalReceiverHavingFile', 0):.2f}%",
            '% Hoàn thành có file': lambda item: f"{item.get('percentTotalCompleteHavingFile', 0):.2f}%",
            '% Tiếp nhận & hoàn thành có file': lambda item: f"{item.get('percentTotalReceiverCompleteHavingFile', 0):.2f}%",
        }
        df = SoBanTableRenderer._build_dataframe(data, columns)
        st.markdown('#### 🔵 Thống kê hồ sơ số hóa')
        st.dataframe(df, use_container_width=True, hide_index=True)

    @staticmethod
    def _format_number(value: int) -> str:
        return f"{value:,}".replace(',', '.')

    @staticmethod
    def _build_dataframe(data: List[Dict], columns: Dict[str, callable]) -> pd.DataFrame:
        display_data = []
        for item in data:
            row = {col_name: func(item) for col_name, func in columns.items()}
            display_data.append(row)
        return pd.DataFrame(display_data)

class ChartRenderer:
    """Class chuyên xử lý việc render biểu đồ"""
    @staticmethod
    def plot_766_barchart(unit_name: str, target_data: Dict[str, float], standard_data: Dict[str, int]):
        comparison_keys = [key for key in target_data.keys() if key != "Điểm tổng"]
        df_chart = pd.DataFrame({
            'Chỉ số': comparison_keys,
            'Điểm đạt được': [target_data[key] for key in comparison_keys],
            'Điểm chuẩn': [standard_data.get(key, 0) for key in comparison_keys]
        })
        df_melted = df_chart.melt(
            id_vars=['Chỉ số'],
            value_vars=['Điểm đạt được', 'Điểm chuẩn'],
            var_name='Loại điểm',
            value_name='Điểm số'
        )
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
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        ChartRenderer._render_comparison_table(df_chart)

    @staticmethod
    def _render_comparison_table(df_chart: pd.DataFrame):
        st.subheader("📊 Bảng so sánh chi tiết")
        df_comparison = df_chart.copy()
        df_comparison['Tỷ lệ đạt (%)'] = (
            df_comparison['Điểm đạt được'] / df_comparison['Điểm chuẩn'] * 100
        ).round(1)
        df_comparison['Chênh lệch'] = (
            df_comparison['Điểm đạt được'] - df_comparison['Điểm chuẩn']
        ).round(1)
        def evaluate_score(ratio):
            if ratio >= 100:
                return "✅ Đạt chuẩn"
            elif ratio >= 80:
                return "⚠️ Gần đạt"
            else:
                return "❌ Chưa đạt"
        df_comparison['Đánh giá'] = df_comparison['Tỷ lệ đạt (%)'].apply(evaluate_score)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)

# Hàm gọi API và hiện bảng danh sách agency
# def render_agency_ids_table(selected_tthc_id: str):
#     st.subheader("📋 Danh sách ID cơ quan Sở/Ban có mã tương ứng")
#     client = APIClient()
#     result = client.get_agency_name_code_list()
#     if not result or "content" not in result:
#         st.info("Không lấy được danh sách cơ quan.")
#         return
#     agencies = result["content"]
#     if not agencies or not isinstance(agencies, list):
#         st.info("Danh sách cơ quan rỗng.")
#         return
#     # Lọc các cơ quan có code trùng selected_tthc_id và lấy chỉ field 'id'
#     filtered_ids = [item.get("id") for item in agencies if item.get("code") == selected_tthc_id and "id" in item]
#     if not filtered_ids:
#         st.info(f"Không tìm thấy cơ quan có mã: {selected_tthc_id}")
#         return
#     # Tạo DataFrame chỉ chứa cột ID
#     df = pd.DataFrame(filtered_ids, columns=["id"])
#     st.dataframe(df, use_container_width=True, hide_index=True)

def render_expander_kgg_chitiet(from_date, to_date, agency_id=None):
    with st.expander("🚀 Xem số liệu chi tiết trên Hệ thống giải quyết TTHC An Giang", expanded=True):
        with st.spinner("⏳ Đang tải dữ liệu KGG..."):
            client = APIClient()
            # Nếu có agency_id thì lấy báo cáo chi tiết cho cơ quan đó
            if agency_id:
                kgg_chitiet = client.get_kgg_report(from_date, to_date, agency_id=agency_id)
                kgg_online = client.get_kgg_online_report(from_date, to_date, agency_id=agency_id)
                kgg_digit = client.get_digitization_report(from_date, to_date, ancestor_id=agency_id)
            else:
                kgg_chitiet = client.get_kgg_report(from_date, to_date)
                kgg_online = client.get_kgg_online_report(from_date, to_date)
                kgg_digit = client.get_digitization_report(from_date, to_date)

            if kgg_chitiet:
                # st.subheader("🟢 Báo cáo hồ sơ một cửa (KGG)")
                SoBanTableRenderer.render_chitiet_table(kgg_chitiet)
            else:
                st.info("Chưa có dữ liệu KGG hồ sơ tổng hợp.")

            if kgg_online:
                # st.subheader("🟠 Báo cáo hồ sơ trực tuyến (KGG)")
                SoBanTableRenderer.render_online_table(kgg_online)
            else:
                st.info("Chưa có dữ liệu KGG hồ sơ trực tuyến.")

            if kgg_digit:
                # st.subheader("🔵 Báo cáo số hóa hồ sơ (KGG)")
                SoBanTableRenderer.render_digitization_table(kgg_digit)
            else:
                st.info("Chưa có dữ liệu KGG số hóa.")


# Cách lấy agency_id từ render_agency_ids_table và dùng trong render_expander_kgg_chitiet
def render_soban_view(data, from_date, to_date):
    renderer = SoBanViewRenderer(data)
    renderer.render()
    st.divider()

    # Lấy agency_id mỗi lần render (tương ứng Sở/Ban đang chọn)
    client = APIClient()
    result = client.get_agency_name_code_list()
    agencies = result.get("content", []) if result else []

    filtered_ids = [
        item.get("id")
        for item in agencies
        if item.get("code") == renderer.selected_tthc_id and "id" in item
    ]

    agency_id = filtered_ids[0] if filtered_ids else None

    # Hiển thị bảng danh sách id cơ quan (luôn phản ánh chọn mới)
    # if filtered_ids:
    #     df = pd.DataFrame(filtered_ids, columns=["id"])
    #     st.subheader("📋 Danh sách ID cơ quan Sở/Ban có mã tương ứng")
    #     st.dataframe(df, use_container_width=True, hide_index=True)
    # else:
    #     st.info(f"Không tìm thấy cơ quan có mã: {renderer.selected_tthc_id}")

    # Gọi hàm expander - luôn truyền agency_id mới nhất
    render_expander_kgg_chitiet(from_date, to_date, agency_id)
