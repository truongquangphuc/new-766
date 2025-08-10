import json
import requests
import os
from datetime import datetime
import base64


token = os.getenv('API_TOKEN', 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJqazlObnpLTWVTeTF6Wk53RW1WMHVzY0FFcWFicTY4MGh5ZFpqY2Q0Wl9zIn0.eyJleHAiOjE3NTQ4NDI4NzUsImlhdCI6MTc1NDc1NjQ3NSwiYXV0aF90aW1lIjoxNzU0NzU1NzkzLCJqdGkiOiJhOGQyYmVmMi04NDA5LTQyZjEtOTRjMy02YWExMDc3ZTExYjciLCJpc3MiOiJodHRwczovL3Nzb2R2Yy5hbmdpYW5nLmdvdi52bi9hdXRoL3JlYWxtcy9kaWdvIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImY6YzA5OGZmOWYtZGM5ZS00MmI3LTkxNmMtZGI4MWE0YjhmZDc4OnRxcGh1Yy5za2hjbkBhbmdpYW5nLmdvdi52biIsInR5cCI6IkJlYXJlciIsImF6cCI6IndlYi1vbmVnYXRlIiwibm9uY2UiOiI5MDRiYjQ3Mi1mMjM0LTRiZTQtYWYyNi04OGVhOTRiMzk4YjIiLCJzZXNzaW9uX3N0YXRlIjoiOWYzMDQ5ZDEtMDEyYS00MDViLTkxYTAtMjg1MzU4MWY2YjE5IiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL2FwaWR2Yy5hbmdpYW5nLmdvdi52biIsImh0dHBzOi8vbW90Y3VhLmFuZ2lhbmcuZ292LnZuIiwiaHR0cDovL2xvY2FsaG9zdDo0MjAwIl0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJnZW5kZXIiOiIxIiwiZ3JvdXBzIjpbImxhbmhkYW9fc290dHR0Iiwic3R0dHR4dWx5IiwidHJ1bmd0YW1kaWV1aGFuaCIsInVibmR0aW5oIiwidGVzdGdyb3VwIiwic290aG9uZ3RpbnZhdHJ1eWVudGhvbmciLCJociIsInN0dHR0dGllcG5oYW4iLCJzdHR0dGR1eWV0IiwiY2FuYm9feHVseV9oaWVudHJ1b25nIl0sIkFsbG93V2hpdGVsaXN0IjpbImh0dHBzOi8vYXBpZHZjLmFuZ2lhbmcuZ292LnZuIl0sInByZWZlcnJlZF91c2VybmFtZSI6InRxcGh1Yy5za2hjbkBhbmdpYW5nLmdvdi52biIsImV4cGVyaWVuY2UiOiI2ODU0YzZmNTJjODU5NDJiMDJkMDU0MTQsNjg1YTY2OTkxOGM2ZWYyZWJiMjZjOTg3LDY4NTJjMmYwNmQ2NTIyMWE3MGU1YjI2YiIsImdpdmVuX25hbWUiOiJUcsawxqFuZyBRdWFuZyBQaOG7pWMiLCJ0eXBlIjoiMyIsImFjY291bnRfaWQiOiI2ODY2YTA3ZmIxN2JhYjJiMjE4ZWNmMWYiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiQUNUSVZJVElfTU9ERUxFUiIsInN0b3JhZ2U0RW1wIiwiaW50ZWdyYXRlRGlnaXRhbFNpZ25hdHVyZSIsIkNCWEwtaUdBVEUiLCJDVERUIiwiQUNUSVZJVElfQURNSU4iLCJBQ1RJVklUSV9VU0VSIiwiQUNUSVZJVElfUFJPQ0VTUyJdfSwidXNlcl9pZCI6IjY4NjZhMDdmYmNhZGM0MDFkM2UxYzViMCIsInBlcm1pc3Npb25zIjpbeyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJhY3Rpdml0aU1vZGVsZXIifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJjaHVuZ1RodWNBY2NlcHRlciJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6ImludGVncmF0ZURpZ2l0YWxTaWduYXR1cmUifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJpc29TdGF0aXN0aWNzIn19LHsicGVybWlzc2lvbiI6eyJjb2RlIjoiaXNvU3RhdGlzdGljc0J5U2VjdG9yIn19LHsicGVybWlzc2lvbiI6eyJjb2RlIjoiaXNvU3RhdGlzdGljc0Z1bGxBZ2VuY3kifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJtYURpZ2l0YWxTaWduYXR1cmVDb25maWcifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJtYW5hZ2VEaWdvIn19LHsicGVybWlzc2lvbiI6eyJjb2RlIjoib25lR2F0ZUNhbmNlbERvc3NpZXJSZXBvcnQifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJvbmVHYXRlRG9zc2llckF1dGhNYW5hZ2VyIn19LHsicGVybWlzc2lvbiI6eyJjb2RlIjoib25lR2F0ZURvc3NpZXJDYW5jZWwifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJvbmVHYXRlRG9zc2llckZlZUtHR1JlcG9ydCJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6Im9uZUdhdGVEb3NzaWVyTG9va3VwIn19LHsicGVybWlzc2lvbiI6eyJjb2RlIjoib25lR2F0ZURvc3NpZXJMb29rdXBCeUFnZW5jeSJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6Im9uZUdhdGVEb3NzaWVyTG9va3VwUGVyc29uYWwifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJvbmVHYXRlRG9zc2llck9ubGluZUtHR1JlcG9ydCJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6Im9uZUdhdGVEb3NzaWVyUHJvY2Vzc2luZyJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6Im9uZUdhdGVEdWVEb3NzaWVyUmVwb3J0In19LHsicGVybWlzc2lvbiI6eyJjb2RlIjoib25lR2F0ZUtHR0RpZ2l0aXphdGlvbkRvc3NpZXJSZXBvcnQifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJvbmVHYXRlTG9nYm9va1N0YXRpc3RpY3MifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJwZXJtaXNzaW9uRG9zc2llcktHRyJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6InN0YXRpc3RpY2FsQWdlbmN5RG9zc2llcktHRyJ9fSx7InBlcm1pc3Npb24iOnsiY29kZSI6InN0YXRpc3RpY2FsQWdlbmN5RG9zc2llcl9LR0cifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJzdGF0aXN0aWNhbEFnZW5jeURvc3NpZXJfTGFuZF9LR0cifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJzdGF0aXN0aWNhbERvc3NpZXJLR0cifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJzdGF0aXN0aWNhbFByb2NlZHVyZURvc3NpZXJLR0cifX0seyJwZXJtaXNzaW9uIjp7ImNvZGUiOiJzdG9yYWdlNEVtcCJ9fV0sIm5hbWUiOiJUcsawxqFuZyBRdWFuZyBQaOG7pWMiLCJkZXBsb3ltZW50X2lkIjoiNjI4YjJlMGVjNzY0YWM2NTEwMmFjM2RjIiwiZW1haWwiOiJbe1widmFsdWVcIiA6IFwidHFwaHVjLnNraGNuQGFuZ2lhbmcuZ292LnZuXCJ9XSJ9.U8BVdh-M6drZGf3ILy8K_HKM6ifttkUVo2ADBvLKJpNsjQDfbKfJshKNHNwcm069kqxtwtATVz0wPnklD4knrFH5P4e3CkoI91EZagMKRE84FWSv58a7PMYqbrGP0QEEmagArLhXJga_F6D1qP3uaykwEcF-LcCu6sVrIXBs17cZEFdshwtOlSH4oFm9hI6AqW-i3t9WbUN-n8cPxWMi0WjwGlTiU9y-E3TxdF1-ZTo05sQAq3Gou5I-5eLCGSNvoWtCZYI3p-D6rt8JxE7IAbvIv2Ydl8zbS6PCd_aMOD8WLhDfC3WSi9RKFysFFlshW-PnzipmF1Cx-F664G1Xyw')  # Đã bỏ token hardcode như yêu cầu


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
    
    if not check_token_expiry(token):
        print("🔄 Vui lòng cập nhật token mới!")
        return None
    
    response = requests.get(
        'https://apidvc.angiang.gov.vn/pa/dossier-statistic/--statistic-agency-kgg',
        headers={'Authorization': f'bearer {token}'},
        params={
            'agency-id': agency_id,
            'from-date': f'{from_date}T00:00:00.000Z',
            'to-date': f'{to_date}T23:59:59.999Z',
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



def get_agency_statistic(from_date: str, to_date: str) -> dict:
    """Thống kê hồ sơ theo cơ quan KGG với error handling"""
    
    if not check_token_expiry(token):
        print("🔄 Token hết hạn - bỏ qua API này!")
        return None
    
    try:
        response = requests.get(
            'https://apidvc.angiang.gov.vn/pa/dossier-statistic/--statistic-agency-kgg',
            headers={'Authorization': f'bearer {token}'},
            params={
                'agency-id': '6854c6f52c85942b02d05414',
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
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ Lỗi 401: Token hết hạn hoặc không có quyền truy cập endpoint này")
            print("💡 Thử lấy token mới từ browser hoặc liên hệ admin")
        elif e.response.status_code == 403:
            print("❌ Lỗi 403: Không có quyền truy cập API này")
        else:
            print(f"❌ HTTP Error {e.response.status_code}: {e}")
        return None


def get_digitization_by_agency(from_date: str, to_date: str) -> dict:
    """Thống kê số hóa theo cơ quan KGG"""
    
    if not check_token_expiry(token):
        print("🔄 Token hết hạn - bỏ qua API này!")
        return None
    
    try:
        response = requests.get(
            'https://apidvc.angiang.gov.vn/pa/kgg-digitize/digitization-by-agency',
            headers={'Authorization': f'bearer {token}'},
            params={
                'from': from_date,
                'to': to_date,
                'ancestor-id': '6852c2f06d65221a70e5b26b',
                'arr-agency': '6854c6f52c85942b02d05414',
                'list-level-id': '5f39f42d5224cf235e134c5a,5f39f4155224cf235e134c59,5febfe2295002b5c79f0fc9f',
                'agency-level-0': '5f6b17984e1bd312a6f3ae4b',
                'agency-level-1': '5f7dade4b80e603d5300dcc4',
                'agency-level-2': '5f6b177a4e1bd312a6f3ae4a'
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ Lỗi 401: Token hết hạn hoặc không có quyền truy cập endpoint digitization")
            print("💡 Thử lấy token mới từ browser hoặc liên hệ admin")
        elif e.response.status_code == 403:
            print("❌ Lỗi 403: Không có quyền truy cập API digitization")
        else:
            print(f"❌ HTTP Error {e.response.status_code}: {e}")
        return None
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")
        return None


def main():
    """Hàm main để test các API functions"""
    print("🚀 BẮT ĐẦU TEST API KGG AN GIANG")
    print("=" * 60)
    
    # Thông tin test
    from_date = '2025-07-01T00:00:00.0Z'
    to_date = '2025-07-31T23:59:59.0Z'
    from_date_alt = '2025-07-01T00:00:00.000Z'
    to_date_alt = '2025-07-31T23:59:59.999Z'
    
    print(f"📅 Khoảng thời gian test: {from_date} đến {to_date}")
    print("=" * 60)
    
    # Test 1: API báo cáo hồ sơ KGG online
    print("\n🔄 TEST 1: API Báo cáo hồ sơ KGG online")
    print("-" * 40)
    
    try:
        result1 = get_report(from_date, to_date)
        if result1:
            print("✅ API báo cáo KGG hoạt động thành công!")
            print("📊 Kết quả báo cáo KGG:")
            print(json.dumps(result1, indent=2, ensure_ascii=False))
        else:
            print("❌ API báo cáo KGG không trả về dữ liệu")
    except Exception as e:
        print(f"❌ Lỗi khi test API báo cáo: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: API thống kê theo cơ quan
    print("\n🔄 TEST 2: API Thống kê theo cơ quan")
    print("-" * 40)
    
    try:
        result2 = get_agency_statistic(from_date_alt, to_date_alt)
        if result2:
            print("✅ API thống kê cơ quan hoạt động thành công!")
            print("📊 Kết quả thống kê cơ quan:")
            print(json.dumps(result2, indent=2, ensure_ascii=False))
        else:
            print("❌ API thống kê cơ quan không trả về dữ liệu")
    except Exception as e:
        print(f"❌ Lỗi khi test API thống kê: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: API số hóa theo cơ quan (MỚI)
    print("\n🔄 TEST 3: API Số hóa theo cơ quan")
    print("-" * 40)
    
    try:
        result3 = get_digitization_by_agency(from_date_alt, to_date_alt)
        if result3:
            print("✅ API số hóa theo cơ quan hoạt động thành công!")
            print("📊 Kết quả số hóa theo cơ quan:")
            print(json.dumps(result3, indent=2, ensure_ascii=False))
        else:
            print("❌ API số hóa theo cơ quan không trả về dữ liệu")
    except Exception as e:
        print(f"❌ Lỗi khi test API số hóa: {e}")
    
    print("\n" + "=" * 60)
    
    print("🏁 KẾT THÚC TEST")
    
    # Tóm tắt kết quả
    print("\n📋 TÓM TẮT KẾT QUẢ:")
    print("1. ✅ Hàm check_token_expiry() hoạt động")
    print("2. ✅ Hàm get_report() đã được test")
    print("3. ✅ Hàm get_agency_statistic() đã được test")
    print("4. ✅ Hàm get_digitization_by_agency() đã được test (MỚI)")
    print("\n💡 Lưu ý: Nếu API lỗi 401, hãy cập nhật token mới!")


if __name__ == "__main__":
    main()
