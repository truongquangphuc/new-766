import requests

# ---- Khai báo thông tin dùng chung ----
URL = 'https://dichvucong.gov.vn/jsp/rest.jsp'
HEADERS = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8,af;q=0.7,sv;q=0.6',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://dichvucong.gov.vn',
    'Referer': 'https://dichvucong.gov.vn/p/home/dvc-index-tinhthanhpho-tonghop.html',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

def fetch_766_angiang_info(target_id="398126"):
    """
    Lấy thông tin chỉ số 766 tổng hợp của tỉnh An Giang từ dữ liệu toàn quốc (data1).
    Trả về dict đã chuẩn hóa.
    """
    data1 = {
        'params': '{"type":"ref","p_nam":"2025","p_6thang":0,"p_tinh_id":0,"pageIndex":1,"pageSize":100,"p_loaidonvi":1,"loaichitieu":0,"service":"report_tinh_766_service","p_quy":0,"p_thang":0}'
    }
    resp1 = requests.post(URL, headers=HEADERS, data=data1)
    json1 = resp1.json()
    # Lấy thông tin tỉnh An Giang
    an_giang = next((item for item in json1 if item['ID'] == target_id), None)
    if not an_giang:
        return None
    # Chuẩn hóa trường
    target = {
        "Công khai, minh bạch": float(an_giang['CKMB']),
        "Tiến độ giải quyết": float(an_giang['TDGQ']),
        "Dịch vụ công trực tuyến": float(an_giang['TTTT']),
        "Thanh toán trực tuyến": float(an_giang['CLGQ']),
        "Mức độ hài lòng": float(an_giang['MDHL']),
        "Số hóa hồ sơ": float(an_giang['MDSH']),
        "Điểm tổng": float(an_giang['TONG_SCORE']),
    }
    return {"target": target, "raw": an_giang}

def fetch_766_all_units_in_province(target_id="398126"):
    """
    Lấy tất cả thông tin các đơn vị trực thuộc trong tỉnh An Giang (data2).
    Trả về list dict (raw).
    """
    data2 = {
        'params': f'{{"type":"ref","p_nam":"2025","p_6thang":0,"p_tinh_id":"{target_id}","pageIndex":1,"pageSize":100,"p_loaidonvi":1,"loaichitieu":0,"service":"report_tinh_766_service","p_quy":0,"p_thang":0}}'
    }
    resp2 = requests.post(URL, headers=HEADERS, data=data2)
    try:
        json2 = resp2.json()
    except Exception as e:
        print("Lỗi khi đọc dữ liệu các đơn vị trong tỉnh:", e)
        print("Raw text:", resp2.text)
        return None
    return json2

# ---- Ví dụ sử dụng ----
if __name__ == "__main__":
    angi_info = fetch_766_angiang_info()
    print("Thông tin tổng hợp tỉnh An Giang:")
    print(angi_info)

    print("\nTất cả đơn vị trong tỉnh An Giang:")
    all_units = fetch_766_all_units_in_province()
    if all_units:
        for item in all_units:
            print(item)
    else:
        print("Không có dữ liệu các đơn vị trực thuộc.")
