import json
import requests
import os
from datetime import datetime
import base64
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

token = os.getenv('API_TOKEN', 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJqazlObnpLTWVTeTF6Wk53RW1WMHVzY0FFcWFicTY4MGh5ZFpqY2Q0Wl9zIn0.eyJleHAiOjE3NTQ4OTc0NTIsImlhdCI6MTc1NDgxMTA1MiwiYXV0aF90aW1lIjoxNzU0ODExMDUxLCJqdGkiOiIzZWFmODhkYi00NDY5LTRiYTktYjI0Yi1jZWIwYTc0OTk4OTkiLCJpc3MiOiJodHRwczovL3Nzb2R2Yy5hbmdpYW5nLmdvdi52bi9hdXRoL3JlYWxtcy9kaWdvIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImY6YzA5OGZmOWYtZGM5ZS00MmI3LTkxNmMtZGI4MWE0YjhmZDc4OnRxcGh1Yy5za2hjbkBhbmdpYW5nLmdvdi52biIsInR5cCI6IkJlYXJlciIsImF6cCI6IndlYi1vbmVnYXRlIiwibm9uY2UiOiIyNjU1ZWUyZC0zNmNhLTQ4OTgtODEyNS1hZTc3NGIwZGExYmEiLCJzZXNzaW9uX3N0YXRlIjoiM2E0ZGQ4MmEtODhkMi00MDA5LWFiM2MtNjE5NWM3NjhhNmRhIiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL2FwaWR2Yy5hbmdpYW5nLmdvdi52biIsImh0dHBzOi8vbW90Y3VhLmFuZ2lhbmcuZ292LnZuIiwiaHR0cDovL2xvY2FsaG9zdDo0MjAwIl0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJnZW5kZXIiOiIxIiwiZ3JvdXBzIjpbImxhbmhkYW9fc290dHR0Iiwic3R0dHR4dWx5IiwidHJ1bmd0YW1kaWV1aGFuaCIsInVibmR0aW5oIiwidGVzdGdyb3VwIiwic290aG9uZ3RpbnZhdHJ1eWVudGhvbmciLCJociIsInN0dHR0dGllcG5oYW4iLCJzdHR0dGR1eWV0IiwiY2FuYm9feHVseV9oaWVudHJ1b25nIl0sIkFsbG93V2hpdGVsaXN0IjpbImh0dHBzOi8vYXBpZHZjLmFuZ2lhbmcuZ292LnZuIl0sInByZWZlcnJlZF91c2VybmFtZSI6InRxcGh1Yy5za2hjbkBhbmdpYW5nLmdvdi52biIsImV4cGVyaWVuY2UiOiI2ODU0YzZmNTJjODU5NDJiMDJkMDU0MTQsNjg1YTY2OTkxOGM2ZWYyZWJiMjZjOTg3LDY4NTJjMmYwNmQ2NTIyMWE3MGU1YjI2YiIsImdpdmVuX25hbWUiOiJUcsawxqFuZyBRdWFuZyBQaOG7pWMiLCJ0eXBlIjoiMyIsImFjY291bnRfaWQiOiI2ODY2YTA3ZmIxN2JhYjJiMjE4ZWNmMWYiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiQUNUSVZJVElfTU9ERUxFUiIsInN0b3JhZ2U0RW1wIiwiaW50ZWdyYXRlRGlnaXRhbFNpZ25hdHVyZSIsIkNCWEwtaUdBVEUiLCJDVERUIiwiQUNUSVZJVElfQURNSU4iLCJBQ1RJVklUSV9VU0VSIiwiQUNUSVZJVElfUFJPQ0VTUyJdfSwidXNlcl9pZCI6IjY4NjZhMDdmYmNhZGM0MDFkM2UxYzViMCIsInBlcm1pc3Npb25zIjpbeyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJhY3Rpdml0aU1vZGVsZXIifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJjaHVuZ1RodWNBY2NlcHRlciJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6ImludGVncmF0ZURpZ2l0YWxTaWduYXR1cmUifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJpc29TdGF0aXN0aWNzIn19LHsicGVybWlzc2lvbiI6eyJjb2RlIjoiaXNvU3RhdGlzdGljc0J5U2VjdG9yIn19LHsicGVybWlzc2lvbiI6eyJjb2RlIjoiaXNvU3RhdGlzdGljc0Z1bGxBZ2VuY3kifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJtYURpZ2l0YWxTaWduYXR1cmVDb25maWcifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJtYW5hZ2VEaWdvIn19LHsicGVybWlzc2lvbiI6eyJjb2RlIjoib25lR2F0ZUNhbmNlbERvc3NpZXJSZXBvcnQifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJvbmVHYXRlRG9zc2llckF1dGhNYW5hZ2VyIn19LHsicGVybWlzc2lvbiI6eyJjb2RlIjoib25lR2F0ZURvc3NpZXJDYW5jZWwifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJvbmVHYXRlRG9zc2llckZlZUtHR1JlcG9ydCJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6Im9uZUdhdGVEb3NzaWVyTG9va3VwIn19LHsicGVybWlzc2lvbiI6eyJjb2RlIjoib25lR2F0ZURvc3NpZXJMb29rdXBCeUFnZW5jeSJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6Im9uZUdhdGVEb3NzaWVyTG9va3VwUGVyc29uYWwifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJvbmVHYXRlRG9zc2llck9ubGluZUtHR1JlcG9ydCJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6Im9uZUdhdGVEb3NzaWVyUHJvY2Vzc2luZyJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6Im9uZUdhdGVEdWVEb3NzaWVyUmVwb3J0In19LHsicGVybWlzc2lvbiI6eyJjb2RlIjoib25lR2F0ZUtHR0RpZ2l0aXphdGlvbkRvc3NpZXJSZXBvcnQifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJvbmVHYXRlTG9nYm9va1N0YXRpc3RpY3MifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJwZXJtaXNzaW9uRG9zc2llcktHRyJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6InN0YXRpc3RpY2FsQWdlbmN5RG9zc2llcktHRyJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6InN0YXRpc3RpY2FsQWdlbmN5RG9zc2llcl9LR0cifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJzdGF0aXN0aWNhbEFnZW5jeURvc3NpZXJfTGFuZF9LR0cifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJzdGF0aXN0aWNhbERvc3NpZXJLR0cifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJzdGF0aXN0aWNhbFByb2NlZHVyZURvc3NpZXJLR0cifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJzdG9yYWdlNEVtcCJ9fV0sIm5hbWUiOiJUcsawxqFuZyBRdWFuZyBQaOG7pWMiLCJkZXBsb3ltZW50X2lkIjoiNjI4YjJlMGVjNzY0YWM2NTEwMmFjM2RjIiwiZW1haWwiOiJbe1widmFsdWVcIiA6IFwidHFwaHVjLnNraGNuQGFuZ2lhbmcuZ292LnZuXCJ9XSJ9.ffo3up9S7x0kWDwfotk45pX-0npjGigx7xT5s2YvJGS81OglZWOAJIq0gsCpSK9toEO0JTTWzCN01RRJrtfqPYHwRUNCevRhww6OyItYX6UnXkTB2eM1ztM24L5GEsANKTyeUZfuKiHb00BEkDA21CUHJAsLzLA-teAKcPz-vEg1EbuKMSScSWupFmh5aPnkaJOE9w6Hl5f4ERljrqx-qJ38fvdsWBwbAcKNyNG28OjyUnSzcPFTshF2i5fc7fn41fk-I_bZX4V02p22rrYLvmqGamHdmgVSAbbWXUYhH47eQXW_t4MqAFS-aHKtgKSxOhdaObECy9mSJC2xfDo-nA')


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
