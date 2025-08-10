import requests
import json


def make_dcv_request(service, **kwargs):
    """Hàm chung để gửi request tới API dichvucong.gov.vn"""
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    # Tham số mặc định
    default_params = {
        "type": "ref",
        "p_nam": "2025",
        "p_tinh_id": "11358",
        "p_huyen_id": "",
        "service": service
    }
    
    # Cập nhật với tham số tùy chỉnh
    default_params.update(kwargs)
    
    data = {"params": json.dumps(default_params)}
    
    try:
        response = requests.post(
            "https://dichvucong.gov.vn/jsp/rest.jsp",
            headers=headers,
            data=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi: {e}")
        return None


def get_tthc_data(p_nam="2025", p_tinh_id="11358", p_xa_id="0", p_6thang=0, p_quy=0, p_thang=0):
    """Lấy dữ liệu TTHC chi tiết"""
    return make_dcv_request(
        service="report_tile_cungcap_dvctt_service",
        p_nam=p_nam,
        p_tinh_id=p_tinh_id,
        p_6thang=p_6thang,
        pageIndex=1,
        pageSize=1000,
        p_default=0,
        p_xa_id=p_xa_id,
        p_quy=p_quy,
        p_thang=p_thang
    )


def get_yearly_summary_data(p_nam="2025", p_tinh_id="11358"):
    """Lấy dữ liệu báo cáo tổng hợp"""
    return make_dcv_request(
        service="report_by_year_sum_service",
        p_nam=p_nam,
        p_tinh_id=p_tinh_id,
        p_linhvuc=0
    )

def get_monthly_summary_data(p_nam="2025", p_tinh_id="11358", p_huyen_id="", p_thang="0", p_linhvuc=0):
    """Lấy dữ liệu báo cáo tổng hợp theo tháng"""
    return make_dcv_request(
        service="report_by_month_sum_service",
        p_nam=p_nam,
        p_tinh_id=p_tinh_id,
        p_huyen_id=p_huyen_id,
        p_thang=p_thang,
        p_linhvuc=p_linhvuc
    )



def get_diem_tonghop(p_nam="2025", p_tinh_id="11358"):
    """Lấy dữ liệu báo cáo điểm tổng hợp"""
    return make_dcv_request(
        service="report_sum_xuonghuongdiem_tonghop_service",
        p_nam=p_nam,
        p_tinh_id=p_tinh_id,
        pageIndex=1,
        pageSize=1000,
        p_default=0
    )


def get_tthc_tilexulyhs(p_nam="2025", p_tinh_id="11358", p_xa_id="0", p_6thang=0, p_quy=0, p_thang=0):
    """Lấy dữ liệu báo cáo tỷ lệ xử lý hồ sơ TTHC theo thời gian"""
    return make_dcv_request(
        service="report_tthc_tilexulyhs_service",
        p_nam=p_nam,
        p_tinh_id=p_tinh_id,
        p_6thang=p_6thang,
        pageIndex=1,
        pageSize=1000,
        p_default=0,
        p_xa_id=p_xa_id,
        p_quy=p_quy,
        p_thang=p_thang
    )


def get_xuhuongdiem_data_sorted(p_nam="2025", p_tinh_id="11358", p_xa_id="0", p_6thang=0, p_quy=0, p_thang=0):
    """Lấy dữ liệu báo cáo xu hướng điểm và sort theo tháng"""
    result = make_dcv_request(
        service="report_xuhuongdiem_service",
        p_nam=p_nam,
        p_tinh_id=p_tinh_id,
        p_6thang=p_6thang,
        pageIndex=1,
        pageSize=1000,
        p_default=0,
        p_xa_id=p_xa_id,
        p_quy=p_quy,
        p_thang=p_thang
    )
    
    # Sort theo MONTH nếu có dữ liệu
    if result and isinstance(result, list):
        result = sorted(result, key=lambda x: int(x.get('MONTH', 0)))
    
    return result


def get_xuhuongdiem_chiso(p_nam="2025", p_tinh_id="11358", p_xa_id="0", p_6thang=0, p_quy=0, p_thang=0):
    """Lấy dữ liệu báo cáo xu hướng điểm chỉ số"""
    return make_dcv_request(
        service="report_xuhuongdiem_chiso_service",
        p_nam=p_nam,
        p_tinh_id=p_tinh_id,
        p_6thang=p_6thang,
        pageIndex=1,
        pageSize=1000,
        p_default=0,
        p_xa_id=p_xa_id,
        p_quy=p_quy,
        p_thang=p_thang
    )


def get_tinh_766_report(p_nam="2025", p_tinh_id="398126", p_6thang=0, p_quy=0, p_thang=0, p_loaidonvi=1, loaichitieu=0):
    """Lấy dữ liệu báo cáo tỉnh 766"""
    return make_dcv_request(
        service="report_tinh_766_service",
        p_nam=p_nam,
        p_tinh_id=p_tinh_id,
        p_6thang=p_6thang,
        pageIndex=1,
        pageSize=1000,
        p_loaidonvi=p_loaidonvi,
        loaichitieu=loaichitieu,
        p_quy=p_quy,
        p_thang=p_thang
    )

def get_tinh_766_report_filtered(p_nam="2025", p_tinh_id="398126", p_6thang=0, p_quy=0, p_thang=0, p_loaidonvi=1, loaichitieu=0, capdonviid="1"):
    """Lấy danh sách ID và TEN từ báo cáo tỉnh 766 với bộ lọc CAPDONVIID"""
        # Gọi API gốc
    result = make_dcv_request(
        service="report_tinh_766_service",
        p_nam=p_nam,
        p_tinh_id=p_tinh_id,
        p_6thang=p_6thang,
        pageIndex=1,
        pageSize=1000,
        p_loaidonvi=p_loaidonvi,
        loaichitieu=loaichitieu,
        p_quy=p_quy,
        p_thang=p_thang
    )
    
    # Xử lý kết quả trả về
    data_list = []
    if isinstance(result, list):
        data_list = result
    elif isinstance(result, dict) and 'data' in result:
        data_list = result.get('data', [])
    # Lọc theo CAPDONVIID nếu có
    original_count = len(data_list)
    if capdonviid is not None:
        data_list = [item for item in data_list if item.get("CAPDONVIID") == capdonviid]
    
    # Chỉ lấy ID và TEN
    final_result = [{"MA_COQUAN": item.get("MA_COQUAN"), "TEN": item.get("TEN")} for item in data_list]
    return final_result




def get_diem_tonghop_v2(p_nam=2024, p_tinh_id="11358", p_huyen_id=""):
    """Lấy dữ liệu báo cáo điểm tổng hợp phiên bản 2 (với tham số số nguyên cho năm)"""
    return make_dcv_request(
        service="report_sum_xuonghuongdiem_tonghop_service",
        p_nam=p_nam,
        p_tinh_id=p_tinh_id,
        p_huyen_id=p_huyen_id,
        pageIndex=1,
        pageSize=1000,
        p_default=0
    )


# Chạy và in kết quả
if __name__ == "__main__":
    print("=== Dữ liệu TTHC chi tiết ===")
    result1 = get_tthc_data()
    if result1:
        print(json.dumps(result1, ensure_ascii=False, indent=2))
    else:
        print("❌ Không thể lấy dữ liệu TTHC")
    
    print("\n=== Dữ liệu báo cáo tổng hợp ===")
    result2 = get_yearly_summary_data()
    if result2:
        print(json.dumps(result2, ensure_ascii=False, indent=2))
    else:
        print("❌ Không thể lấy dữ liệu tổng hợp")
    
    print("\n=== Dữ liệu thống kê điểm tổng hợp ===")
    result3 = get_diem_tonghop()
    if result3:
        print(json.dumps(result3, ensure_ascii=False, indent=2))
    else:
        print("❌ Không thể lấy dữ liệu điểm tổng hợp")
    
    print("\n=== Dữ liệu tỷ lệ xử lý hồ sơ TTHC ===")
    result4 = get_tthc_tilexulyhs(p_thang=7)
    if result4:
        print(json.dumps(result4, ensure_ascii=False, indent=2))
    else:
        print("❌ Không thể lấy dữ liệu tỷ lệ xử lý hồ sơ")
    
    print("\n=== Dữ liệu báo cáo xu hướng điểm ===")
    result5 = get_xuhuongdiem_data_sorted()
    if result5:
        print(json.dumps(result5, ensure_ascii=False, indent=2))
    else:
        print("❌ Không thể lấy dữ liệu xu hướng điểm")
    
    print("\n=== Dữ liệu báo cáo xu hướng điểm chỉ số ===")
    result6 = get_xuhuongdiem_chiso()
    if result6:
        print(json.dumps(result6, ensure_ascii=False, indent=2))
    else:
        print("❌ Không thể lấy dữ liệu xu hướng điểm chỉ số")
    
    print("\n=== Dữ liệu báo cáo tỉnh 766 ===")
    result7 = get_tinh_766_report()
    if result7:
        print(f"Số lượng bản ghi: {len(result7)}")
    else:
        print("❌ Không thể lấy dữ liệu báo cáo tỉnh 766")
    
    print("\n=== Dữ liệu điểm tổng hợp v2 (năm 2024) ===")
    result8 = get_diem_tonghop_v2()
    if result8:
        print(json.dumps(result8, ensure_ascii=False, indent=2))
    else:
        print("❌ Không thể lấy dữ liệu điểm tổng hợp v2")
