# TTHC_fetcher.py

import requests
from bs4 import BeautifulSoup

# Function to scrape the website and extract the required data
def fetch_TTHC_data():
    cookies = {
        'route': '175317275.529.252.925341',
        'JSESSIONID': 'B0C393F1D8A26478D99D64A8B0BDBD6C',
        'TS5115beel': '01f5515fee835f98b569ae8d569ae8d569ae8'
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8,af;q=0.7,sv;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Referer': 'https://dichvucong.gov.vn/p/home/dvc-trang-chu.html',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'sec-ch-ua': '"NotA;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
        'Cookie': 'route=175317275.529.252.925341; JSESSIONID=B0C393F1D8A26478D99D64A8B0BDBD6C; TS5115beel=01f5515fee835f98b569ae8d569ae8d569ae8'
    }

    # Send the request
    response = requests.get('https://dichvucong.gov.vn/p/home/dvc-dich-vu-cong-truc-tuyen.html', cookies=cookies, headers=headers)

    # Parse the response HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the header row and extract header names
    header_row = soup.find('tr')
    headers = [th.get_text(strip=True) for th in header_row.find_all('th')]

    # Find all the rows and extract the data for each row
    data_rows = soup.find_all('tr', {'data-coquan-id': '398126'})

    # Prepare a list to hold all data as a list of dictionaries
    data = []
    for row in data_rows:
        columns = row.find_all('td')
        row_data = {headers[i]: columns[i].get_text(strip=True) for i in range(len(columns))}
        data.append(row_data)

    return data
