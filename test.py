from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
from urllib.parse import urlparse, parse_qs

def get_auth_code(username, password, login_url, redirect_uri):
    # Khởi tạo trình duyệt
    driver = webdriver.Chrome()
    driver.get(login_url)

    try:
        # Chờ trang load rồi nhập user, pass (update selectors nếu cần)
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "kc-login").click()

        # Đợi redirect đến redirect_uri có mã code trên URL
        while True:
            curr_url = driver.current_url
            if curr_url.startswith(redirect_uri) and "code=" in curr_url:
                break
            time.sleep(0.5)
        code = parse_qs(urlparse(driver.current_url).query)['code'][0]
        print("Lấy được mã code:", code)
        cookies = driver.get_cookies()
        return code, cookies
    finally:
        driver.quit()

def exchange_code_for_token(code, redirect_uri, client_id, cookies):
    url = "https://ssodvc.angiang.gov.vn/auth/realms/digo/protocol/openid-connect/token"
    data = {
        "grant_type":"authorization_code",
        "client_id": client_id,
        "code": code,
        "redirect_uri": redirect_uri,
    }
    # Chuyển cookies Selenium thành dict chuẩn cho requests
    cookies_dict = {c['name']:c['value'] for c in cookies}
    # Gửi POST lấy token
    response = requests.post(url, data=data, cookies=cookies_dict)
    if response.status_code == 200:
        print("Đăng nhập thành công!")
        print("Access token:", response.json().get("access_token"))
        return response.json()
    else:
        print(f"Lỗi khi lấy token: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    # --- Thông tin cấu hình ---
    USER = "tên đăng nhập của bạn"
    PASS = "mật khẩu của bạn"
    # login_url: trang đăng nhập sẽ redirect qua SSO (lấy ở link từ hệ thống, VD)
    LOGIN_URL = "https://motcua.angiang.gov.vn/vi/..."  # Chỉnh URL login đúng flow
    REDIRECT_URI = "https://motcua.angiang.gov.vn/vi/" # Đúng y redirect_uri client
    CLIENT_ID = "web-onegate"

    code, cookies = get_auth_code(USER, PASS, LOGIN_URL, REDIRECT_URI)
    if code:
        exchange_code_for_token(code, REDIRECT_URI, CLIENT_ID, cookies)
