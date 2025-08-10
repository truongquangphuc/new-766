# test_simple.py
from get_tthc_chitiet import get_report

# Sử dụng agency ID đã biết có dữ liệu
result = get_report("2025-07-01", "2025-07-31", "6852c2f06d65221a70e5b26b")
if result:
    print(f"🎉 SUCCESS! Có {len(result)} records")
    print("First record:", result[0] if result else "None")
else:
    print("❌ No data")
