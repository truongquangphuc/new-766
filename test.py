import requests

def get_token_by_username_password(username, password):
    url = "https://ssodvc.angiang.gov.vn/auth/realms/digo/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": "web-onegate",
        "username": username,
        "password": password,
        "scope": "openid"
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')

        print("Đăng nhập thành công!")
        print("Access Token:", access_token)
        print("Refresh Token:", refresh_token)

        return access_token, refresh_token

    except requests.exceptions.HTTPError as errh:
        print("Lỗi HTTP:", errh)
        print("Chi tiết:", response.text)
    except requests.exceptions.ConnectionError as errc:
        print("Lỗi kết nối:", errc)
    except requests.exceptions.Timeout as errt:
        print("Lỗi timeout:", errt)
    except requests.exceptions.RequestException as err:
        print("Lỗi yêu cầu:", err)

# Ví dụ gọi hàm
if __name__ == "__main__":
    username_input = "tqphuc.skhcn@angiang.gov.vn"
    password_input = "Tz(9eC:xJg<T"

    get_token_by_username_password(username_input, password_input)
