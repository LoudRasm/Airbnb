# Chọn compiler cho báo cáo

Báo cáo dùng fontspec và tiếng Việt Unicode, cần XeLaTeX.

Trên Overleaf:
1. Mở Settings bằng biểu tượng bánh răng (hoặc File > Settings).
2. Chọn Compiler ở thanh bên; tại Compiler chọn XeLaTeX.
3. Main document: Nhom10_InsideAirbnb_Report.tex.
4. Bấm Recompile.

Nếu trước đó đã xóa fontspec, khôi phục report_style.tex gốc từ gói source.
Chỉ xóa fontspec sẽ khiến setmainfont, setmonofont và IfFontExistsTF tiếp tục lỗi.

File latexmkrc đặt mặc định XeLaTeX khi dùng latexmk. Trên Overleaf vẫn chọn compiler trong Settings; đừng chỉ dựa vào dòng % !TeX program trong source.

Máy cá nhân: latexmk -xelatex Nhom10_InsideAirbnb_Report.tex
Hướng dẫn chính thức: https://docs.overleaf.com/getting-started/recompiling-your-project/selecting-a-tex-live-version-and-latex-compiler
