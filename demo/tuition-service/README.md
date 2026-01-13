# Tuition Service

Tuition Service quản lý học phí của sinh viên với logic thanh toán tuần tự (sequential payment).

## Thay đổi so với Student Service cũ

### Database Schema
- ❌ **XÓA:** Bảng `students` riêng biệt
- ✅ **MỚI:** Chỉ còn 1 bảng `tuitions` chứa cả thông tin student và tuition
- ✅ **Trade-off:** Duplicate student info (student_name, student_email) nhưng đơn giản hóa query (không cần JOIN)

### API Changes
- ❌ **XÓA:** `/api/students/*`
- ✅ **MỚI:** `/api/tuitions/*`
- ✅ **MỚI:** Field `canPay` trong mỗi tuition (chỉ tuition cũ nhất chưa đóng = `true`)
- ✅ **MỚI:** Internal API `/get-payable` cho Payment Service

## Endpoints

### 1. POST /search (Public)
Tìm kiếm student và trả về tất cả tuitions với flag `canPay`.

**Request:**
```json
{
  "student_id": "52000123"
}
```

**Response:**
```json
{
  "student": {
    "student_id": "52000123",
    "student_name": "Nguyen Van A",
    "student_email": "52000123@student.tdtu.edu.vn"
  },
  "all_tuitions": [
    {
      "id": 1,
      "student_id": "52000123",
      "semester": 1,
      "academic_year": "2024-2025",
      "fee": 5000000,
      "status": "unpaid",
      "canPay": true
    },
    {
      "id": 2,
      "semester": 2,
      "academic_year": "2024-2025",
      "fee": 5000000,
      "status": "unpaid",
      "canPay": false
    }
  ]
}
```

### 2. POST /get-payable (Internal - Requires API Key)
Lấy tuition cần thanh toán (chỉ Payment Service gọi).

**Headers:**
```
X-API-Key: secret_internal_api_key_12345
```

**Request:**
```json
{
  "student_id": "52000123"
}
```

**Response:**
```json
{
  "success": true,
  "tuition": {
    "id": 1,
    "student_id": "52000123",
    "semester": 1,
    "academic_year": "2024-2025",
    "fee": 5000000,
    "status": "unpaid"
  }
}
```

### 3. POST /:id/mark-paid (Internal - Requires API Key)
Đánh dấu tuition đã thanh toán (chỉ Payment Service gọi).

**Headers:**
```
X-API-Key: secret_internal_api_key_12345
```

**Request:**
```json
{
  "paid": true
}
```

**Response:**
```json
{
  "success": true,
  "tuition": {
    "id": 1,
    "semester": 1,
    "academic_year": "2024-2025",
    "fee": 0,
    "status": "paid"
  }
}
```

## Logic thanh toán tuần tự

1. ✅ Query tuitions: `ORDER BY academic_year ASC, semester ASC`
2. ✅ Tìm tuition chưa đóng CỦ NHẤT (oldest unpaid)
3. ✅ Set `canPay = true` CHỈ cho tuition đó
4. ✅ User chỉ được thanh toán tuition có `canPay = true`
5. ✅ Không thể skip tuition cũ để đóng tuition mới

## Environment Variables

```bash
DATABASE_URL=mysql+pymysql://root:root@tuition_db:3306/tuition_db
INTERNAL_API_KEY=secret_internal_api_key_12345
```

## Run with Docker

```bash
docker-compose up tuition_service tuition_db
```

## Security

- ✅ Internal APIs protected by API Key
- ✅ User không thể can thiệp vào `tuition_id`
- ✅ Backend kiểm soát hoàn toàn thứ tự thanh toán
