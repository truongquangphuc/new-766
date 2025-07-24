import requests

def fetch_766_data(target_id="398126"):
    """
    Lấy dữ liệu chỉ số 766 cho một địa phương theo ID và cho toàn bộ, trả về dict {'all': ..., '398126': ...}
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

    def normalize(raw):
        if not raw: return None
        return {
            "STT": raw.get("ROW_STT"),
            "Tỉnh/Thành phố": raw.get("TEN"),
            "Công khai, minh bạch": float(raw.get("CKMB", 0)),
            "Tiến độ giải quyết": float(raw.get("TDGQ", 0)),
            "Dịch vụ trực tuyến": float(raw.get("TTTT", 0)),
            "Mức độ hài lòng": float(raw.get("MDHL", 0)),
            "Số hóa hồ sơ": float(raw.get("MDSH", 0)),
            "Tổng điểm": float(raw.get("TONG_SCORE", 0))
        }

    try:
        # Lấy toàn bộ, rồi lọc theo target_id
        r1 = requests.post(url, headers=headers, data=data1, timeout=30)
        result_all = None
        if r1.status_code == 200:
            d1 = r1.json()
            if isinstance(d1, list):
                filtered = [item for item in d1 if item.get("ID") == target_id]
                if filtered:
                    result_all = normalize(filtered[0])

        # Lấy riêng tỉnh target_id
        r2 = requests.post(url, headers=headers, data=data2, timeout=30)
        result_398126 = None
        if r2.status_code == 200:
            d2 = r2.json()
            if isinstance(d2, list) and d2:
                result_398126 = normalize(d2[0])

        return {
            "all": result_all,
            target_id: result_398126
        }
    except Exception as e:
        print("Lỗi khi fetch dữ liệu 766:", e)
        return None
