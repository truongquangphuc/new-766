import json
import requests
import os
from datetime import datetime
import base64
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

token = os.getenv('API_TOKEN', '')


def check_token_expiry(token: str):
    """Kiểm tra token có hết hạn không"""
    try:
        # Decode JWT payload
        parts = token.split('.')
        payload = json.loads(base64.b64decode(parts[1] + '=='))
        exp_time = payload['exp']
        current_time = int(datetime.now().timestamp())
        
        if current_time > exp_time:
            print(f"❌ Token đã hết hạn lúc: {datetime.fromtimestamp(exp_time)}")
            return False
        else:
            remaining = exp_time - current_time
            print(f"✅ Token còn hiệu lực {remaining//3600} giờ {(remaining%3600)//60} phút")
            return True
    except Exception as e:
        print(f"❌ Lỗi kiểm tra token: {e}")
        return False


def get_report(from_date: str, to_date: str, agency_id: str = '6852c2f06d65221a70e5b26b') -> dict:
    """Báo cáo hồ sơ KGG online"""
    # Đã có agency_id đúng làm default
    
    if not check_token_expiry(token):
        print("🔄 Vui lòng cập nhật token mới!")
        return None
    
    # Format ngày tự động
    if 'T' not in from_date:
        from_date = f"{from_date}T00:00:00.000Z"
    if 'T' not in to_date:
        to_date = f"{to_date}T23:59:59.999Z"
    
    print(f"📅 Truy vấn: {from_date} -> {to_date}")
    print(f"🏢 Agency: {agency_id}")
    
    response = requests.get(
        'https://apidvc.angiang.gov.vn/pa/dossier-statistic/--statistic-agency-kgg',
        headers={'Authorization': f'bearer {token}'},
        params={
            'agency-id': agency_id,
            'from-date': from_date,
            'to-date': to_date,
            'agencyLevel0': '5f6b17984e1bd312a6f3ae4b',
            'agencyLevel1': '5f7dade4b80e603d5300dcc4',
            'agencyLevel2': '5f6b177a4e1bd312a6f3ae4a',
            'procedureLevel4': '62b529f524023d508ef38fc0',
            'procedureLevel3': '62b529c424023d508ef38fbd',
            'procedureLevel2': '62b52a0224023d508ef38fc1',
            'suppended-cancelled': 'true',
            'hide-agency-no-dossier': 'false',
            'isOnlineAttachResults': 'false',
            'isKGGReportCancel': 'true'
        },
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def create_session_with_retries():
    """Tạo session với retry strategy - Fixed version"""
    session = requests.Session()
    
    # Cấu hình retry strategy với parameter mới
    retry_strategy = Retry(
        total=3,  # Tối đa 3 lần retry
        status_forcelist=[429, 500, 502, 503, 504],  # Retry với các status code này
        allowed_methods=["HEAD", "GET", "OPTIONS"],  # Thay method_whitelist bằng allowed_methods
        backoff_factor=2,  # Tăng delay giữa các retry
        respect_retry_after_header=True  # Tôn trọng Retry-After header từ server
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,  # Số connection pools
        pool_maxsize=20       # Max connections per pool
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def get_report_online(from_date: str, to_date: str, agency_id: str = '6852c2f06d65221a70e5b26b') -> dict:
    """Báo cáo hồ sơ KGG dossier online - Version tối ưu với retry và timeout cao"""
    
    if not check_token_expiry(token):
        print("🔄 Vui lòng cập nhật token mới!")
        return None
    
    # Format ngày tự động
    if 'T' not in from_date:
        from_date = f"{from_date}T00:00:00.0Z"
    if 'T' not in to_date:
        to_date = f"{to_date}T23:59:59.0Z"
    
    print(f"📅 Truy vấn KGG Dossier: {from_date} -> {to_date}")
    print(f"🏢 Agency: {agency_id}")
    
    session = create_session_with_retries()
    
    try:
        print("⏳ Đang gửi request... (có thể mất vài phút)")
        start_time = time.time()
        
        response = session.get(
            'https://apidvc.angiang.gov.vn/pa/kgg-dossier-statistic/--kgg-dossier-report-online',
            headers={
                'Authorization': f'bearer {token}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            },
            params={
                'from-applied-date': from_date,
                'to-applied-date': to_date,
                'agency-id': agency_id,
                'agencyLevel0': '5f6b17984e1bd312a6f3ae4b',
                'agencyLevel1': '5f7dade4b80e603d5300dcc4',
                'agencyLevel2': '5f6b177a4e1bd312a6f3ae4a',
                'procedureLevel4': '62b529f524023d508ef38fc0',
                'procedureLevel3': '62b529c424023d508ef38fbd',
                'procedureLevel2': '62b52a0224023d508ef38fc1',
                'is-ignore-free-dossier': 'true'
            },
            timeout=(30, 180),  # Connect: 30s, Read: 180s (3 phút)
            stream=True  # Stream để tránh memory issues với response lớn
        )
        
        response.raise_for_status()
        
        # Đo thời gian response
        elapsed_time = time.time() - start_time
        print(f"✅ Request thành công! Thời gian: {elapsed_time:.2f}s")
        
        return response.json()
        
    except requests.exceptions.Timeout as e:
        elapsed_time = time.time() - start_time
        print(f"⏰ Timeout sau {elapsed_time:.2f}s: {e}")
        print("💡 Gợi ý: Thử thu nhỏ khoảng thời gian hoặc liên hệ admin để kiểm tra server")
        return None
        
    except requests.exceptions.ConnectionError as e:
        print(f"🌐 Lỗi kết nối mạng: {e}")
        print("💡 Kiểm tra internet hoặc VPN nếu cần")
        return None
        
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 401:
            print("🔐 Lỗi 401: Token hết hạn hoặc không hợp lệ")
        elif status_code == 403:
            print("🚫 Lỗi 403: Không có quyền truy cập")
        elif status_code == 429:
            print("🚦 Lỗi 429: Rate limit - đợi và thử lại")
        elif status_code >= 500:
            print(f"🔧 Lỗi server {status_code}: Vấn đề từ phía API")
        else:
            print(f"❌ HTTP Error {status_code}: {e}")
        return None
        
    except requests.exceptions.JSONDecodeError as e:
        print(f"📄 Lỗi parse JSON: {e}")
        print("💡 Response có thể không phải JSON hoặc bị truncated")
        return None
        
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {type(e).__name__}: {e}")
        return None
        
    finally:
        session.close()



def get_digitization_by_agency(from_date: str, to_date: str, ancestor_id: str = '6852c2f06d65221a70e5b26b') -> dict:
    """Báo cáo số hóa theo cơ quan KGG"""
    
    if not check_token_expiry(token):
        print("🔄 Vui lòng cập nhật token mới!")
        return None
    
    # Format ngày tự động
    if 'T' not in from_date:
        from_date = f"{from_date}T00:00:00.000Z"
    if 'T' not in to_date:
        to_date = f"{to_date}T23:59:59.999Z"
    
    print(f"📅 Truy vấn Digitization: {from_date} -> {to_date}")
    print(f"🏢 Ancestor ID: {ancestor_id}")
    
    session = create_session_with_retries()
    
    try:
        print("⏳ Đang gửi request digitization... (có thể mất vài phút)")
        start_time = time.time()
        
        response = session.get(
            'https://apidvc.angiang.gov.vn/pa/kgg-digitize/digitization-by-agency',
            headers={
                'Authorization': f'bearer {token}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            },
            params={
                'from': from_date,
                'to': to_date,
                'ancestor-id': ancestor_id,
                'list-level-id': '5f39f42d5224cf235e134c5a,5f39f4155224cf235e134c59,5febfe2295002b5c79f0fc9f',
                'agency-level-0': '5f6b17984e1bd312a6f3ae4b',
                'agency-level-1': '5f7dade4b80e603d5300dcc4',
                'agency-level-2': '5f6b177a4e1bd312a6f3ae4a'
            },
            timeout=(30, 180),  # Connect: 30s, Read: 180s
            stream=True
        )
        
        # Log response info
        print(f"📊 Response status: {response.status_code}")
        
        response.raise_for_status()
        
        # Đo thời gian response
        elapsed_time = time.time() - start_time
        print(f"✅ Request digitization thành công! Thời gian: {elapsed_time:.2f}s")
        
        # Parse JSON với error handling
        try:
            data = response.json()
            print(f"📋 Đã nhận được dữ liệu digitization với {len(data) if isinstance(data, (dict, list)) else 'unknown'} items")
            return data
        except ValueError as json_err:
            print(f"📄 Lỗi parse JSON: {json_err}")
            return None
        
    except requests.exceptions.Timeout as e:
        elapsed_time = time.time() - start_time
        print(f"⏰ Timeout sau {elapsed_time:.2f}s: {e}")
        print("💡 Gợi ý: Thử thu nhỏ khoảng thời gian")
        return None
        
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 401:
            print("🔐 Lỗi 401: Token hết hạn hoặc không hợp lệ")
        elif status_code == 403:
            print("🚫 Lỗi 403: Không có quyền truy cập API digitization")
        elif status_code >= 500:
            print(f"🔧 Lỗi server {status_code}: Vấn đề từ phía API")
        else:
            print(f"❌ HTTP Error {status_code}: {e}")
        return None
        
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {type(e).__name__}: {e}")
        return None
        
    finally:
        session.close()

def main():
    """Hàm main để test các API functions"""
    print("🚀 BẮT ĐẦU TEST API KGG AN GIANG")
    print("=" * 60)
    
    # Thông tin test
    from_date = '2025-07-01T00:00:00.0Z'
    to_date = '2025-07-31T23:59:59.0Z'
    
    print(f"📅 Khoảng thời gian test: {from_date} đến {to_date}")
    print("=" * 60)
    
    # Test 1: API báo cáo hồ sơ KGG online
    print("\n🔄 TEST 1: API Báo cáo hồ sơ KGG online")
    print("-" * 40)
    
    try:
        result1 = get_digitization_by_agency(from_date, to_date, ancestor_id="6852c2f06d65221a70e5b26b")
        if result1:
            print("✅ API báo cáo KGG hoạt động thành công!")
            print("📊 Kết quả báo cáo KGG:")
            print(json.dumps(result1, indent=2, ensure_ascii=False))
        else:
            print("❌ API báo cáo KGG không trả về dữ liệu")
    except Exception as e:
        print(f"❌ Lỗi khi test API báo cáo: {e}")
    
    print("\n" + "=" * 60)
    

if __name__ == "__main__":
    main()
