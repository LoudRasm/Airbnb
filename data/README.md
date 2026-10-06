# Quy ước dữ liệu

Raw: data/raw/YYYY-MM-DD/{listings.csv.gz,calendar.csv.gz,reviews.csv.gz,neighbourhoods.geojson}.
Downloader tạo các thư mục theo config. Không commit raw.
Processed: demo/ và real/ tách riêng; mặc định gitignore toàn bộ output. Chỉ thêm dữ liệu sạch
nhỏ dưới 50 MB sau kiểm tra; dùng git add -f đúng file, không bỏ ignore toàn bộ thư mục.
Samples demo là dữ liệu giả; manual_labels.csv header-only chờ nhãn thật.
