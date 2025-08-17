import requests
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging


class DCVService(Enum):
    """Enum chứa các service endpoints"""
    TTHC_DATA = "report_tile_cungcap_dvctt_service"
    YEARLY_SUMMARY = "report_by_year_sum_service"
    MONTHLY_SUMMARY = "report_by_month_sum_service"
    DIEM_TONGHOP = "report_sum_xuonghuongdiem_tonghop_service"
    TTHC_TILEXULYHS = "report_tthc_tilexulyhs_service"
    XUHUONGDIEM = "report_xuhuongdiem_service"
    XUHUONGDIEM_CHISO = "report_xuhuongdiem_chiso_service"
    TINH_766_REPORT = "report_tinh_766_service"


@dataclass
class DCVConfig:
    """Configuration class cho DCV API"""
    BASE_URL = "https://dichvucong.gov.vn/jsp/rest.jsp"
    
    # Default values
    DEFAULT_YEAR = "2025"
    DEFAULT_PROVINCE_ID = "11358"
    DEFAULT_PAGE_INDEX = 1
    DEFAULT_PAGE_SIZE = 1000
    DEFAULT_P_DEFAULT = 0
    
    # Request settings
    REQUEST_TIMEOUT = 30
    
    # Headers
    DEFAULT_HEADERS = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    }


class DCVRequestBuilder:
    """Class xây dựng request parameters"""
    
    @staticmethod
    def build_base_params(service: str, **kwargs) -> Dict[str, Any]:
        """Xây dựng base parameters cho request"""
        base_params = {
            "type": "ref",
            "p_nam": DCVConfig.DEFAULT_YEAR,
            "p_tinh_id": DCVConfig.DEFAULT_PROVINCE_ID,
            "p_huyen_id": "",
            "service": service
        }
        
        # Cập nhật với custom parameters
        base_params.update(kwargs)
        return base_params
    
    @staticmethod
    def build_pagination_params(page_index: int = None, page_size: int = None) -> Dict[str, Any]:
        """Xây dựng pagination parameters"""
        return {
            "pageIndex": page_index or DCVConfig.DEFAULT_PAGE_INDEX,
            "pageSize": page_size or DCVConfig.DEFAULT_PAGE_SIZE,
            "p_default": DCVConfig.DEFAULT_P_DEFAULT
        }
    
    @staticmethod
    def build_time_params(p_6thang: int = 0, p_quy: int = 0, p_thang: int = 0) -> Dict[str, Any]:
        """Xây dựng time parameters"""
        return {
            "p_6thang": p_6thang,
            "p_quy": p_quy,
            "p_thang": p_thang
        }


class DCVHTTPClient:
    """HTTP client cho DCV API"""
    
    def __init__(self):
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Tạo HTTP session với cấu hình tối ưu"""
        session = requests.Session()
        session.headers.update(DCVConfig.DEFAULT_HEADERS)
        return session
    
    def make_request(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Thực hiện HTTP request"""
        data = {"params": json.dumps(params)}
        
        try:
            response = self.session.post(
                DCVConfig.BASE_URL,
                data=data,
                timeout=DCVConfig.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logging.error("Request timeout")
            return None
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            return None
    
    def close(self):
        """Đóng session"""
        self.session.close()


class BaseReportHandler:
    """Base class cho các report handlers"""
    
    def __init__(self, client: DCVHTTPClient):
        self.client = client
        self.request_builder = DCVRequestBuilder()
    
    def _make_service_request(self, service: DCVService, **kwargs) -> Optional[Dict[str, Any]]:
        """Thực hiện request cho service"""
        params = self.request_builder.build_base_params(service.value, **kwargs)
        return self.client.make_request(params)


class TTHCDataHandler(BaseReportHandler):
    """Handler cho TTHC data reports"""
    
    def get_tthc_data(self, p_nam: str = None, p_tinh_id: str = None, 
                      p_xa_id: str = "0", p_6thang: int = 0, 
                      p_quy: int = 0, p_thang: int = 0) -> Optional[Dict[str, Any]]:
        """Lấy dữ liệu TTHC chi tiết"""
        params = {
            "p_nam": p_nam or DCVConfig.DEFAULT_YEAR,
            "p_tinh_id": p_tinh_id or DCVConfig.DEFAULT_PROVINCE_ID,
            "p_xa_id": p_xa_id,
            **self.request_builder.build_time_params(p_6thang, p_quy, p_thang),
            **self.request_builder.build_pagination_params()
        }
        
        return self._make_service_request(DCVService.TTHC_DATA, **params)
    
    def get_tthc_tilexulyhs(self, p_nam: str = None, p_tinh_id: str = None,
                           p_xa_id: str = "0", p_6thang: int = 0, 
                           p_quy: int = 0, p_thang: int = 0) -> Optional[Dict[str, Any]]:
        """Lấy dữ liệu báo cáo tỷ lệ xử lý hồ sơ TTHC theo thời gian"""
        params = {
            "p_nam": p_nam or DCVConfig.DEFAULT_YEAR,
            "p_tinh_id": p_tinh_id or DCVConfig.DEFAULT_PROVINCE_ID,
            "p_xa_id": p_xa_id,
            **self.request_builder.build_time_params(p_6thang, p_quy, p_thang),
            **self.request_builder.build_pagination_params()
        }
        
        return self._make_service_request(DCVService.TTHC_TILEXULYHS, **params)


class SummaryReportHandler(BaseReportHandler):
    """Handler cho summary reports"""
    
    def get_yearly_summary_data(self, p_nam: str = None, p_tinh_id: str = None) -> Optional[Dict[str, Any]]:
        """Lấy dữ liệu báo cáo tổng hợp"""
        params = {
            "p_nam": p_nam or DCVConfig.DEFAULT_YEAR,
            "p_tinh_id": p_tinh_id or DCVConfig.DEFAULT_PROVINCE_ID,
            "p_linhvuc": 0
        }
        
        return self._make_service_request(DCVService.YEARLY_SUMMARY, **params)
    
    def get_monthly_summary_data(self, p_nam: str = None, p_tinh_id: str = None, 
                                p_huyen_id: str = "", p_thang: str = "0", 
                                p_linhvuc: int = 0) -> Optional[Dict[str, Any]]:
        """Lấy dữ liệu báo cáo tổng hợp theo tháng"""
        params = {
            "p_nam": p_nam or DCVConfig.DEFAULT_YEAR,
            "p_tinh_id": p_tinh_id or DCVConfig.DEFAULT_PROVINCE_ID,
            "p_huyen_id": p_huyen_id,
            "p_thang": p_thang,
            "p_linhvuc": p_linhvuc
        }
        
        return self._make_service_request(DCVService.MONTHLY_SUMMARY, **params)


class ScoreReportHandler(BaseReportHandler):
    """Handler cho score reports"""
    
    def get_diem_tonghop(self, p_nam: str = None, p_tinh_id: str = None) -> Optional[Dict[str, Any]]:
        """Lấy dữ liệu báo cáo điểm tổng hợp"""
        params = {
            "p_nam": p_nam or DCVConfig.DEFAULT_YEAR,
            "p_tinh_id": p_tinh_id or DCVConfig.DEFAULT_PROVINCE_ID,
            **self.request_builder.build_pagination_params()
        }
        
        return self._make_service_request(DCVService.DIEM_TONGHOP, **params)
    
    def get_diem_tonghop_v2(self, p_nam: Union[int, str] = 2024, 
                           p_tinh_id: str = None, p_huyen_id: str = "") -> Optional[Dict[str, Any]]:
        """Lấy dữ liệu báo cáo điểm tổng hợp phiên bản 2"""
        params = {
            "p_nam": p_nam,
            "p_tinh_id": p_tinh_id or DCVConfig.DEFAULT_PROVINCE_ID,
            "p_huyen_id": p_huyen_id,
            **self.request_builder.build_pagination_params()
        }
        
        return self._make_service_request(DCVService.DIEM_TONGHOP, **params)


class TrendReportHandler(BaseReportHandler):
    """Handler cho trend reports"""
    
    def get_xuhuongdiem_data_sorted(self, p_nam: str = None, p_tinh_id: str = None,
                                   p_xa_id: str = "0", p_6thang: int = 0, 
                                   p_quy: int = 0, p_thang: int = 0) -> Optional[List[Dict[str, Any]]]:
        """Lấy dữ liệu báo cáo xu hướng điểm và sort theo tháng"""
        params = {
            "p_nam": p_nam or DCVConfig.DEFAULT_YEAR,
            "p_tinh_id": p_tinh_id or DCVConfig.DEFAULT_PROVINCE_ID,
            "p_xa_id": p_xa_id,
            **self.request_builder.build_time_params(p_6thang, p_quy, p_thang),
            **self.request_builder.build_pagination_params()
        }
        
        result = self._make_service_request(DCVService.XUHUONGDIEM, **params)
        
        # Sort theo MONTH nếu có dữ liệu
        if result and isinstance(result, list):
            result = sorted(result, key=lambda x: int(x.get('MONTH', 0)))
        
        return result
    
    def get_xuhuongdiem_chiso(self, p_nam: str = None, p_tinh_id: str = None,
                             p_xa_id: str = "0", p_6thang: int = 0, 
                             p_quy: int = 0, p_thang: int = 0) -> Optional[Dict[str, Any]]:
        """Lấy dữ liệu báo cáo xu hướng điểm chỉ số"""
        params = {
            "p_nam": p_nam or DCVConfig.DEFAULT_YEAR,
            "p_tinh_id": p_tinh_id or DCVConfig.DEFAULT_PROVINCE_ID,
            "p_xa_id": p_xa_id,
            **self.request_builder.build_time_params(p_6thang, p_quy, p_thang),
            **self.request_builder.build_pagination_params()
        }
        
        return self._make_service_request(DCVService.XUHUONGDIEM_CHISO, **params)


class ProvinceReportHandler(BaseReportHandler):
    """Handler cho province 766 reports"""
    
    def get_tinh_766_report(self, p_nam: str = None, p_tinh_id: str = "398126", 
                           p_6thang: int = 0, p_quy: int = 0, p_thang: int = 0,
                           p_loaidonvi: int = 1, loaichitieu: int = 0) -> Optional[Dict[str, Any]]:
        """Lấy dữ liệu báo cáo tỉnh 766"""
        params = {
            "p_nam": p_nam or DCVConfig.DEFAULT_YEAR,
            "p_tinh_id": p_tinh_id,
            "p_loaidonvi": p_loaidonvi,
            "loaichitieu": loaichitieu,
            **self.request_builder.build_time_params(p_6thang, p_quy, p_thang),
            **self.request_builder.build_pagination_params()
        }
        
        return self._make_service_request(DCVService.TINH_766_REPORT, **params)
    
    def get_tinh_766_report_filtered(self, p_nam: str = None, p_tinh_id: str = "398126",
                                   p_6thang: int = 0, p_quy: int = 0, p_thang: int = 0,
                                   p_loaidonvi: int = 1, loaichitieu: int = 0, 
                                   capdonviid: str = "1") -> List[Dict[str, str]]:
        """Lấy danh sách ID và TEN từ báo cáo tỉnh 766 với bộ lọc CAPDONVIID"""
        
        # Gọi API gốc
        result = self.get_tinh_766_report(
            p_nam, p_tinh_id, p_6thang, p_quy, p_thang, 
            p_loaidonvi, loaichitieu
        )
        
        if not result:
            return []
        
        # Xử lý kết quả trả về
        data_list = self._extract_data_list(result)
        
        # Lọc theo CAPDONVIID nếu có
        if capdonviid is not None:
            data_list = [item for item in data_list if item.get("CAPDONVIID") == capdonviid]
        # Chỉ lấy MA_COQUAN và TEN
        # return [
        #     {"MA_COQUAN": item.get("MA_COQUAN"), "TEN": item.get("TEN")} 
        #     for item in data_list
        # ]
        return data_list
    
    def _extract_data_list(self, result: Union[List, Dict]) -> List[Dict]:
        """Trích xuất data list từ result"""
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and 'data' in result:
            return result.get('data', [])
        return []


class DCVAPIClient:
    """Main API client class - điều phối tất cả các handlers"""
    
    def __init__(self):
        self.http_client = DCVHTTPClient()
        self.tthc_handler = TTHCDataHandler(self.http_client)
        self.summary_handler = SummaryReportHandler(self.http_client)
        self.score_handler = ScoreReportHandler(self.http_client)
        self.trend_handler = TrendReportHandler(self.http_client)
        self.province_handler = ProvinceReportHandler(self.http_client)

    # TTHC Data methods
    def get_tthc_data(
        self,
        p_nam: str = "2025",
        p_tinh_id: str = "11358",
        p_xa_id: str = "0",
        p_6thang: int = 0,
        p_quy: int = 0,
        p_thang: int = 0
    ) -> Optional[Dict[str, Any]]:
        """Lấy dữ liệu TTHC chi tiết"""
        return self.tthc_handler.get_tthc_data(
            p_nam, p_tinh_id, p_xa_id, p_6thang, p_quy, p_thang
        )

    def get_tthc_tilexulyhs(
        self,
        p_nam: str = "2025",
        p_tinh_id: str = "11358",
        p_xa_id: str = "0",
        p_6thang: int = 0,
        p_quy: int = 0,
        p_thang: int = 0
    ) -> Optional[Dict[str, Any]]:
        return self.tthc_handler.get_tthc_tilexulyhs(
            p_nam, p_tinh_id, p_xa_id, p_6thang, p_quy, p_thang
        )

    # Summary methods
    def get_yearly_summary_data(
        self,
        p_nam: str = "2025",
        p_tinh_id: str = "11358"
    ) -> Optional[Dict[str, Any]]:
        return self.summary_handler.get_yearly_summary_data(p_nam, p_tinh_id)

    def get_monthly_summary_data(
        self,
        p_nam: str = "2025",
        p_tinh_id: str = "11358",
        p_huyen_id: str = "",
        p_thang: str = "0",
        p_linhvuc: int = 0
    ) -> Optional[Dict[str, Any]]:
        return self.summary_handler.get_monthly_summary_data(
            p_nam, p_tinh_id, p_huyen_id, p_thang, p_linhvuc
        )

    # Score methods
    def get_diem_tonghop(
        self,
        p_nam: str = "2025",
        p_tinh_id: str = "11358"
    ) -> Optional[Dict[str, Any]]:
        return self.score_handler.get_diem_tonghop(p_nam, p_tinh_id)

    def get_diem_tonghop_v2(
        self,
        p_nam: Union[int, str] = 2024,
        p_tinh_id: str = "11358",
        p_huyen_id: str = ""
    ) -> Optional[Dict[str, Any]]:
        return self.score_handler.get_diem_tonghop_v2(p_nam, p_tinh_id, p_huyen_id)

    # Trend methods
    def get_xuhuongdiem_data_sorted(
        self,
        p_nam: str = "2025",
        p_tinh_id: str = "11358",
        p_xa_id: str = "0",
        p_6thang: int = 0,
        p_quy: int = 0,
        p_thang: int = 0
    ) -> Optional[List[Dict[str, Any]]]:
        return self.trend_handler.get_xuhuongdiem_data_sorted(
            p_nam, p_tinh_id, p_xa_id, p_6thang, p_quy, p_thang
        )

    def get_xuhuongdiem_chiso(
        self,
        p_nam: str = "2025",
        p_tinh_id: str = "11358",
        p_xa_id: str = "0",
        p_6thang: int = 0,
        p_quy: int = 0,
        p_thang: int = 0
    ) -> Optional[Dict[str, Any]]:
        return self.trend_handler.get_xuhuongdiem_chiso(
            p_nam, p_tinh_id, p_xa_id, p_6thang, p_quy, p_thang
        )

    # Province methods
    def get_tinh_766_report(
        self,
        p_nam: str = "2025",
        p_tinh_id: str = "398126",
        p_6thang: int = 0,
        p_quy: int = 0,
        p_thang: int = 0,
        p_loaidonvi: int = 1,
        loaichitieu: int = 0
    ) -> Optional[Dict[str, Any]]:
        return self.province_handler.get_tinh_766_report(
            p_nam, p_tinh_id, p_6thang, p_quy, p_thang, p_loaidonvi, loaichitieu
        )

    def get_tinh_766_report_filtered(
        self,
        p_nam: str = "2025",
        p_tinh_id: str = "398126",
        p_6thang: int = 0,
        p_quy: int = 0,
        p_thang: int = 0,
        p_loaidonvi: int = 1,
        loaichitieu: int = 0,
        capdonviid: str = "1"
    ) -> List[Dict[str, str]]:
        return self.province_handler.get_tinh_766_report_filtered(
            p_nam, p_tinh_id, p_6thang, p_quy, p_thang, p_loaidonvi, loaichitieu, capdonviid
        )

    def close(self):
        self.http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DCVAPITester:
    """Class để test các API functions"""
    
    def __init__(self, client: DCVAPIClient):
        self.client = client
    
    def run_all_tests(self):
        """Chạy tất cả tests"""
        test_configs = [
            ("=== Dữ liệu TTHC chi tiết ===", self.client.get_tthc_data, {}),
            ("=== Dữ liệu báo cáo tổng hợp ===", self.client.get_yearly_summary_data, {}),
            ("=== Dữ liệu thống kê điểm tổng hợp ===", self.client.get_diem_tonghop, {}),
            ("=== Dữ liệu tỷ lệ xử lý hồ sơ TTHC ===", self.client.get_tthc_tilexulyhs, {"p_thang": 7}),
            ("=== Dữ liệu báo cáo xu hướng điểm ===", self.client.get_xuhuongdiem_data_sorted, {}),
            ("=== Dữ liệu báo cáo xu hướng điểm chỉ số ===", self.client.get_xuhuongdiem_chiso, {}),
            ("=== Dữ liệu báo cáo tỉnh 766 ===", self.client.get_tinh_766_report, {}),
            ("=== Dữ liệu điểm tổng hợp v2 (năm 2024) ===", self.client.get_diem_tonghop_v2, {})
        ]
        
        for title, test_func, params in test_configs:
            self._run_single_test(title, test_func, params)
    
    def _run_single_test(self, title: str, test_func, params: Dict[str, Any]):
        """Chạy một test cụ thể"""
        print(title)
        try:
            result = test_func(**params)
            if result:
                if isinstance(result, list):
                    if "766" in title:
                        print(f"Số lượng bản ghi: {len(result)}")
                    else:
                        print(json.dumps(result, ensure_ascii=False, indent=2))
                else:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"❌ Không thể lấy dữ liệu cho {title}")
        except Exception as e:
            print(f"❌ Lỗi khi test {title}: {e}")
        print()


# Entry point functions - tương thích với code cũ
def make_dcv_request(service: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Entry point tương thích - hàm chung để gửi request tới API"""
    with DCVAPIClient() as client:
        params = DCVRequestBuilder.build_base_params(service, **kwargs)
        return client.http_client.make_request(params)


def get_tthc_data(p_nam: str = "2025", p_tinh_id: str = "11358", p_xa_id: str = "0", 
                  p_6thang: int = 0, p_quy: int = 0, p_thang: int = 0) -> Optional[Dict[str, Any]]:
    """Entry point tương thích - lấy dữ liệu TTHC chi tiết"""
    with DCVAPIClient() as client:
        return client.get_tthc_data(
            p_nam=p_nam,
            p_tinh_id=p_tinh_id,
            p_xa_id=p_xa_id,
            p_6thang=p_6thang,
            p_quy=p_quy,
            p_thang=p_thang
        )



def get_yearly_summary_data(p_nam: str = "2025", p_tinh_id: str = "11358") -> Optional[Dict[str, Any]]:
    """Entry point tương thích - lấy dữ liệu báo cáo tổng hợp"""
    with DCVAPIClient() as client:
        return client.get_yearly_summary_data(p_nam=p_nam, p_tinh_id=p_tinh_id)


def get_monthly_summary_data(p_nam: str = "2025", p_tinh_id: str = "11358", 
                           p_huyen_id: str = "", p_thang: str = "0", 
                           p_linhvuc: int = 0) -> Optional[Dict[str, Any]]:
    """Entry point tương thích - lấy dữ liệu báo cáo tổng hợp theo tháng"""
    with DCVAPIClient() as client:
        return client.get_monthly_summary_data(p_nam=p_nam, p_tinh_id=p_tinh_id,
                                              p_huyen_id=p_huyen_id, p_thang=p_thang,
                                              p_linhvuc=p_linhvuc)


def get_diem_tonghop(p_nam: str = "2025", p_tinh_id: str = "11358") -> Optional[Dict[str, Any]]:
    """Entry point tương thích - lấy dữ liệu báo cáo điểm tổng hợp"""
    with DCVAPIClient() as client:
        return client.get_diem_tonghop(p_nam=p_nam, p_tinh_id=p_tinh_id)


def get_tthc_tilexulyhs(p_nam: str = "2025", p_tinh_id: str = "11358", p_xa_id: str = "0",
                       p_6thang: int = 0, p_quy: int = 0, p_thang: int = 0) -> Optional[Dict[str, Any]]:
    """Entry point tương thích - lấy dữ liệu tỷ lệ xử lý hồ sơ TTHC"""
    with DCVAPIClient() as client:
        return client.get_tthc_tilexulyhs(p_nam=p_nam, p_tinh_id=p_tinh_id, p_xa_id=p_xa_id,
                                         p_6thang=p_6thang, p_quy=p_quy, p_thang=p_thang)


def get_xuhuongdiem_data_sorted(p_nam: str = "2025", p_tinh_id: str = "11358", p_xa_id: str = "0",
                               p_6thang: int = 0, p_quy: int = 0, p_thang: int = 0) -> Optional[List[Dict[str, Any]]]:
    """Entry point tương thích - lấy dữ liệu xu hướng điểm đã sort"""
    with DCVAPIClient() as client:
        return client.get_xuhuongdiem_data_sorted(p_nam=p_nam, p_tinh_id=p_tinh_id, p_xa_id=p_xa_id,
                                                 p_6thang=p_6thang, p_quy=p_quy, p_thang=p_thang)


def get_xuhuongdiem_chiso(p_nam: str = "2025", p_tinh_id: str = "11358", p_xa_id: str = "0",
                         p_6thang: int = 0, p_quy: int = 0, p_thang: int = 0) -> Optional[Dict[str, Any]]:
    """Entry point tương thích - lấy dữ liệu xu hướng điểm chỉ số"""
    with DCVAPIClient() as client:
        return client.get_xuhuongdiem_chiso(p_nam=p_nam, p_tinh_id=p_tinh_id, p_xa_id=p_xa_id,
                                           p_6thang=p_6thang, p_quy=p_quy, p_thang=p_thang)


def get_tinh_766_report(p_nam: str = "2025", p_tinh_id: str = "398126", p_6thang: int = 0,
                       p_quy: int = 0, p_thang: int = 0, p_loaidonvi: int = 1, 
                       loaichitieu: int = 0) -> Optional[Dict[str, Any]]:
    """Entry point tương thích - lấy dữ liệu báo cáo tỉnh 766"""
    with DCVAPIClient() as client:
        return client.get_tinh_766_report(p_nam=p_nam, p_tinh_id=p_tinh_id, p_6thang=p_6thang,
                                         p_quy=p_quy, p_thang=p_thang, p_loaidonvi=p_loaidonvi,
                                         loaichitieu=loaichitieu)


def get_tinh_766_report_filtered(p_nam: str = "2025", p_tinh_id: str = "398126", p_6thang: int = 0,
                                p_quy: int = 0, p_thang: int = 0, p_loaidonvi: int = 1,
                                loaichitieu: int = 0, capdonviid: str = "1") -> List[Dict[str, str]]:
    """Entry point tương thích - lấy dữ liệu báo cáo tỉnh 766 đã lọc"""
    with DCVAPIClient() as client:
        return client.get_tinh_766_report_filtered(p_nam=p_nam, p_tinh_id=p_tinh_id, p_6thang=p_6thang,
                                                  p_quy=p_quy, p_thang=p_thang, p_loaidonvi=p_loaidonvi,
                                                  loaichitieu=loaichitieu, capdonviid=capdonviid)


def get_diem_tonghop_v2(p_nam: Union[int, str] = 2024, p_tinh_id: str = "11358", 
                       p_huyen_id: str = "") -> Optional[Dict[str, Any]]:
    """Entry point tương thích - lấy dữ liệu điểm tổng hợp v2"""
    with DCVAPIClient() as client:
        return client.get_diem_tonghop_v2(p_nam=p_nam, p_tinh_id=p_tinh_id, p_huyen_id=p_huyen_id)


def main():
    """Entry point chính - tương thích với code cũ"""
    with DCVAPIClient() as client:
        tester = DCVAPITester(client)
        tester.run_all_tests()


if __name__ == "__main__":
    main()
