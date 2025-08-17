import streamlit as st
from datetime import datetime, date
from typing import Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import logging
import calendar
from typing import List, Dict, Any

# Import các client classes đã tối ưu
from get_tthc_ketqua import DCVAPIClient
from get_tthc_chitiet import APIClient as KGGAPIClient


class DataType(Enum):
    """Enum cho các loại dữ liệu"""
    TTHC = "tthc"
    YEARLY_SUMMARY = "yearly_summary"
    MONTHLY_SUMMARY = "monthly_summary"
    DIEM_TONGHOP = "diem_tonghop"
    TILEXULY = "tilexuly"
    XUHUONG = "xuhuong"
    CHISO = "chiso"
    REPORT_766 = "report_766"
    REPORT_766_SO_NGANH = "766_report_filtered_so_nganh"
    REPORT_766_XA = "766_report_filtered_xa"
    REPORT_CHITIET = "report_chitiet"
    REPORT_CHITIET_ONLINE = "report_chitiet_online"
    REPORT_DIGITIZATION = "report_digitization"
    TINH_766_REPORT = "report_tinh_766_service"


@dataclass
class LoaderConfig:
    """Configuration cho data loader"""
    # Cache settings
    CACHE_TTL = 300  # 5 phút
    
    # Default values
    DEFAULT_XA_ID = "0"
    DEFAULT_766_PROVINCE_ID = "398126"
    DEFAULT_KGG_AGENCY_ID = "6852c2f06d65221a70e5b26b"
    
    # Filter values
    SO_NGANH_FILTER = "1"
    XA_FILTER = "2"


class DateRangeCalculator:
    """Class tính toán date range"""
    
    @staticmethod
    def calculate_date_range(year: int, p_thang: int) -> Tuple[str, str]:
        """Tính toán from_date và to_date dựa trên năm và tháng"""
        if p_thang == 0:  # Cả năm
            from_date = f"{year}-01-01"
            to_date = f"{year}-12-31"
        else:  # Theo tháng cụ thể
            last_day = DateRangeCalculator._get_last_day_of_month(year, p_thang)
            from_date = f"{year}-{p_thang:02d}-01"
            to_date = f"{year}-{p_thang:02d}-{last_day}"
        
        return from_date, to_date
    
    @staticmethod
    def _get_last_day_of_month(year: int, month: int) -> int:
        """Lấy ngày cuối tháng"""
        return calendar.monthrange(year, month)[1]


class DataValidator:
    """Class validate dữ liệu"""
    
    @staticmethod
    def validate_parameters(year: int, tinh_id: str, p_6thang: int, 
                          p_quy: int, p_thang: int) -> bool:
        """Validate các parameters đầu vào"""
        if not isinstance(year, int) or year < 2020 or year > 2030:
            logging.error(f"Invalid year: {year}")
            return False
        
        if not tinh_id or not isinstance(tinh_id, str):
            logging.error(f"Invalid tinh_id: {tinh_id}")
            return False
        
        if p_thang < 0 or p_thang > 12:
            logging.error(f"Invalid p_thang: {p_thang}")
            return False
        
        return True
    
    @staticmethod
    def validate_data_result(data: Dict[str, Any]) -> bool:
        """Validate kết quả data đã load"""
        if not data:
            logging.error("Data is empty")
            return False
        
        # Kiểm tra các key bắt buộc
        required_keys = [
            DataType.MONTHLY_SUMMARY.value,
            DataType.REPORT_766.value
        ]
        
        for key in required_keys:
            if key not in data:
                logging.warning(f"Missing required key: {key}")
        
        return True


class DCVDataLoader:
    """Loader cho DCV data"""
    
    def __init__(self, client: DCVAPIClient):
        self.client = client
    
    def load_dcv_data(self, year: str, tinh_id: str, p_6thang: int, 
                     p_quy: int, p_thang: int) -> Dict[str, Any]:
        """Load tất cả DCV data"""
        dcv_data = {}
        
        # Basic data
        dcv_data[DataType.TTHC.value] = self.client.get_tthc_data(
            year, tinh_id, LoaderConfig.DEFAULT_XA_ID, p_6thang, p_quy, p_thang
        )
        
        dcv_data[DataType.YEARLY_SUMMARY.value] = self.client.get_yearly_summary_data(
            year, tinh_id
        )
        
        dcv_data[DataType.MONTHLY_SUMMARY.value] = self.client.get_monthly_summary_data(
            p_nam=year, p_tinh_id=tinh_id, p_thang=str(p_thang)
        )
        
        # Score data
        dcv_data[DataType.DIEM_TONGHOP.value] = self.client.get_diem_tonghop(
            year, tinh_id
        )
        
        # Analysis data
        dcv_data[DataType.TILEXULY.value] = self.client.get_tthc_tilexulyhs(
            year, tinh_id, LoaderConfig.DEFAULT_XA_ID, p_6thang, p_quy, p_thang
        )
        
        dcv_data[DataType.XUHUONG.value] = self.client.get_xuhuongdiem_data_sorted(
            year, tinh_id, LoaderConfig.DEFAULT_XA_ID, p_6thang, p_quy, p_thang
        )
        
        dcv_data[DataType.CHISO.value] = self.client.get_xuhuongdiem_chiso(
            year, tinh_id, LoaderConfig.DEFAULT_XA_ID, p_6thang, p_quy, p_thang
        )
        
        # 766 Reports
        dcv_data[DataType.REPORT_766.value] = self.client.get_tinh_766_report(
            year, LoaderConfig.DEFAULT_766_PROVINCE_ID, p_6thang, p_quy, p_thang
        )
        
        dcv_data[DataType.REPORT_766_SO_NGANH.value] = self.client.get_tinh_766_report_filtered(
            year, LoaderConfig.DEFAULT_766_PROVINCE_ID, p_6thang, p_quy, p_thang, 
            capdonviid=LoaderConfig.SO_NGANH_FILTER
        )
        
        dcv_data[DataType.REPORT_766_XA.value] = self.client.get_tinh_766_report_filtered(
            year, LoaderConfig.DEFAULT_766_PROVINCE_ID, p_6thang, p_quy, p_thang, 
            capdonviid=LoaderConfig.XA_FILTER
        )

        dcv_data[DataType.TINH_766_REPORT.value] = self.client.get_tinh_766_report(
            year, '0', p_6thang, p_quy, p_thang
        )
        
        return dcv_data

class KGGDataLoader:
    """Loader cho KGG data"""
    def __init__(self, client):
        self.client = client

    def get_kgg_report(self, from_date: str, to_date: str, agency_id: str = None):
        """Lấy báo cáo tổng hợp KGG"""
        return self.client.get_kgg_report(from_date, to_date, agency_id)

    def get_kgg_online_report(self, from_date: str, to_date: str, agency_id: str = None):
        """Lấy báo cáo KGG online"""
        return self.client.get_kgg_online_report(from_date, to_date, agency_id)

    def get_digitization_report(self, from_date: str, to_date: str, ancestor_id: str = None):
        """Lấy báo cáo số hoá theo agency"""
        return self.client.get_digitization_report(from_date, to_date, ancestor_id)


class DataLoaderOrchestrator:
    """Main orchestrator cho data loading"""
    
    def __init__(self):
        self.date_calculator = DateRangeCalculator()
        self.validator = DataValidator()
    
    def load_all_data(self, year: int, tinh_id: str, p_6thang: int, p_quy: int, p_thang: int) -> Optional[Dict[str, Any]]:
        try:
            # Validate parameters
            if not self.validator.validate_parameters(year, tinh_id, p_6thang, p_quy, p_thang):
                st.error("Tham số đầu vào không hợp lệ")
                return None

            # Chỉ load DCV (quốc gia)
            all_data = {}
            with DCVAPIClient() as dcv_client:
                dcv_loader = DCVDataLoader(dcv_client)
                dcv_data = dcv_loader.load_dcv_data(str(year), tinh_id, p_6thang, p_quy, p_thang)
                all_data.update(dcv_data)

            # KHÔNG load KGG mặc định nữa! 
            # Muốn dùng, tự tạo client, gọi loader ở ngoài UI hoặc view

            # Validate result
            if not self.validator.validate_data_result(all_data):
                st.warning("Một số dữ liệu có thể bị thiếu")
            return all_data

        except Exception as e:
            logging.error(f"Error loading data: {e}")
            st.error(f"Lỗi khi tải dữ liệu: {e}")
            return None

class NumberFormatter:
    """Utility class cho format số"""
    
    @staticmethod
    def format_number(number: Union[int, float, None], decimal_places: int = 0) -> str:
        """Format số với dấu chấm phân cách"""
        if number is None:
            return "0"
        
        try:
            if decimal_places == 0:
                return f"{int(number):,}".replace(',', '.')
            else:
                return f"{float(number):,.{decimal_places}f}".replace(',', '.')
        except (ValueError, TypeError):
            return "0"
    
    @staticmethod
    def format_percentage(number: Union[int, float, None], decimal_places: int = 1) -> str:
        """Format phần trăm"""
        if number is None:
            return "0%"
        
        try:
            return f"{float(number):.{decimal_places}f}%"
        except (ValueError, TypeError):
            return "0%"
    
    @staticmethod
    def format_currency(number: Union[int, float, None], currency: str = "VND") -> str:
        """Format tiền tệ"""
        if number is None:
            return f"0 {currency}"
        
        try:
            formatted = f"{int(number):,}".replace(',', '.')
            return f"{formatted} {currency}"
        except (ValueError, TypeError):
            return f"0 {currency}"


class CachedDataLoader:
    """Wrapper class với caching support"""
    
    def __init__(self):
        self.orchestrator = DataLoaderOrchestrator()
    
    @st.cache_data(ttl=LoaderConfig.CACHE_TTL)
    def load_all_data_cached(_self, year: int, tinh_id: str, p_6thang: int, 
                            p_quy: int, p_thang: int) -> Optional[Dict[str, Any]]:
        """Load data với cache support"""
        return _self.orchestrator.load_all_data(year, tinh_id, p_6thang, p_quy, p_thang)


# Singleton instance cho cached loader
_cached_loader_instance = None


def get_cached_loader() -> CachedDataLoader:
    """Get singleton instance của cached loader"""
    global _cached_loader_instance
    if _cached_loader_instance is None:
        _cached_loader_instance = CachedDataLoader()
    return _cached_loader_instance


# Entry point functions - tương thích với code cũ
def calculate_date_range(year: int, p_thang: int) -> Tuple[str, str]:
    """Entry point tương thích - tính toán date range"""
    return DateRangeCalculator.calculate_date_range(year, p_thang)


@st.cache_data(ttl=LoaderConfig.CACHE_TTL)
def load_all_data(year: int, tinh_id: str, p_6thang: int, 
                 p_quy: int, p_thang: int) -> Optional[Dict[str, Any]]:
    """Entry point tương thích - load all data với cache"""
    loader = get_cached_loader()
    return loader.load_all_data_cached(year, tinh_id, p_6thang, p_quy, p_thang)


def format_number(number: Union[int, float, None], decimal_places: int = 0) -> str:
    """Entry point tương thích - format number"""
    return NumberFormatter.format_number(number, decimal_places)


# Additional utility functions
def format_percentage(number: Union[int, float, None], decimal_places: int = 1) -> str:
    """Format percentage - new utility function"""
    return NumberFormatter.format_percentage(number, decimal_places)


def format_currency(number: Union[int, float, None], currency: str = "VND") -> str:
    """Format currency - new utility function"""
    return NumberFormatter.format_currency(number, currency)


def clear_data_cache():
    """Clear data cache"""
    st.cache_data.clear()


def get_data_loading_status(data: Dict[str, Any]) -> Dict[str, bool]:
    """Get status của từng loại dữ liệu"""
    status = {}
    for data_type in DataType:
        key = data_type.value
        status[key] = key in data and data[key] is not None
    return status


def log_data_loading_summary(data: Dict[str, Any]):
    """Log summary của data loading"""
    status = get_data_loading_status(data)
    successful = sum(1 for success in status.values() if success)
    total = len(status)
    
    logging.info(f"Data loading summary: {successful}/{total} successful")
    
    # Log failed items
    failed_items = [key for key, success in status.items() if not success]
    if failed_items:
        logging.warning(f"Failed to load: {', '.join(failed_items)}")


class DataLoaderManager:
    """Manager class cho advanced data loading operations"""
    
    def __init__(self):
        self.orchestrator = DataLoaderOrchestrator()
    
    def load_data_with_retry(self, year: int, tinh_id: str, p_6thang: int, 
                           p_quy: int, p_thang: int, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Load data với retry mechanism"""
        for attempt in range(max_retries):
            try:
                data = self.orchestrator.load_all_data(year, tinh_id, p_6thang, p_quy, p_thang)
                if data:
                    log_data_loading_summary(data)
                    return data
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
        
        return None
    
    def load_partial_data(self, year: int, tinh_id: str, p_6thang: int, 
                         p_quy: int, p_thang: int, data_types: List[DataType]) -> Dict[str, Any]:
        """Load chỉ một số loại dữ liệu cụ thể"""
        # Implementation cho partial data loading
        # Có thể implement sau nếu cần
        raise NotImplementedError("Partial data loading not implemented yet")


def main():
    """Test function cho data loader"""
    # Test basic functionality
    loader = DataLoaderOrchestrator()
    
    # Test date calculation
    from_date, to_date = calculate_date_range(2025, 7)
    print(f"Date range for July 2025: {from_date} to {to_date}")
    
    # Test number formatting
    print(f"Formatted number: {format_number(1234567.89, 2)}")
    print(f"Formatted percentage: {format_percentage(85.67)}")
    print(f"Formatted currency: {format_currency(1000000)}")


if __name__ == "__main__":
    main()
