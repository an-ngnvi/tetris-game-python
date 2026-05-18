# 🎮 Classic Tetris Game (Python)

**Đồ án môn học:** Lập trình Python  
**Học kỳ - Năm học:** Học kỳ 1 (2024 - 2025) | Năm 2  
**Trường:** Đại học Sư phạm Kỹ thuật TP.HCM (HCMUTE)  
**GVHD:** TS. Phan Thị Thể  
**Nhóm:** 13 – Lớp IPPA233277_08  

---

## 📝 Giới thiệu dự án
Dự án xây dựng lại trò chơi Xếp gạch (Tetris) cổ điển sử dụng ngôn ngữ lập trình Python và thư viện đồ họa pygame. Trò chơi có đầy đủ cơ chế gốc: di chuyển, xoay khối, xóa hàng, tính điểm và tăng tốc độ theo độ khó. Ngoài ra còn bổ sung các tính năng mới như phá hủy khối bằng chuột, bảng xếp hạng, và hiệu ứng pháo hoa.

---

## ✨ Tính năng nổi bật
* 7 loại khối Tetromino (S, Z, I, O, J, L, T) với màu sắc riêng biệt
* 3 mức độ khó: Easy, Normal, Hard
* Tính năng phá hủy khối bằng chuột với hiệu ứng nhấp nháy
* Xem trước khối tiếp theo
* Bảng xếp hạng lưu điểm theo tên người chơi (top 10)
* Hiệu ứng pháo hoa khi đạt top 1 hoặc top 5
* Nhạc nền và âm thanh nút bấm

---

## 🛠️ Công nghệ sử dụng
* **Ngôn ngữ:** Python 3.10+
* **Thư viện chính:** Pygame, Random, Math, Pathlib
* **Công cụ:** Git & GitHub

---

## 🎮 Hướng dẫn chơi

| Phím / Thao tác | Chức năng |
| :--- | :--- |
| **`←`** / **`→`** | Di chuyển khối sang trái / phải |
| **`↑`** | Xoay khối |
| **`↓`** | Rơi nhanh |
| **`Space`** | Rơi thẳng xuống đáy |
| **`P`** | Tạm dừng / Tiếp tục |
| **Click chuột trái** | Phá hủy vùng 3×3 (tối đa 3 lần/ván) |

---

## 🚀 Hướng dẫn cài đặt & Chạy game

1. **Tải mã nguồn về máy:**
   ```bash
   git clone [https://github.com/an-ngnvi/tetris-game-python.git](https://github.com/an-ngnvi/tetris-game-python.git)
   cd tetris-game-python