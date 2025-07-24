import requests

def fetch_766_data(target_id="398126"):
    """
    Lấy dữ liệu chỉ số 766 cho một địa phương, dữ liệu trung bình toàn quốc, dịch vụ công trực tuyến (loaichitieu=2),
    và thanh toán trực tuyến (loaichitieu=3). Trả về dict với 4 modal đã chuẩn hóa.
    """
    url = 'https://dichvucong.gov.vn/jsp/rest.jsp'
    headers = {
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

    # Request 1: toàn bộ (p_tinh_id=0)
    data1 = {
        'params': '{"type":"ref","p_nam":"2025","p_6thang":0,"p_tinh_id":0,"pageIndex":1,"pageSize":100,"p_loaidonvi":1,"loaichitieu":0,"service":"report_tinh_766_service","p_quy":0,"p_thang":0}'
    }
    # Request 2: chỉ tỉnh target_id
    data2 = {
        'params': f'{{"type":"ref","p_nam":"2025","p_6thang":0,"p_tinh_id":"{target_id}","pageIndex":1,"pageSize":100,"p_loaidonvi":1,"loaichitieu":0,"service":"report_tinh_766_service","p_quy":0,"p_thang":0}}'
    }

    # Gửi request 1: chỉ tỉnh target_id
    resp1 = requests.post(url, headers=headers, data=data1)
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