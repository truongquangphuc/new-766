Mỗi lần sửa code xong, chỉ cần:

git add .
git commit -m "Nội dung commit"
git push


Cấu trúc dự án:

project/
├── dashboard.py              # View tổng (main)
├── views/
│   ├── __init__.py
│   ├── tinh_view.py         # View cấp tỉnh  
│   ├── soban_view.py        # View sở ban ngành
│   └── xa_view.py           # View cấp xã
├── utils/
│   ├── __init__.py
│   ├── data_loader.py       # Hàm load dữ liệu
│   └── config.py            # Cấu hình chung
├── get_tthc_data.py         # API functions
└── requirements.txt