# Báo cáo đóng góp cá nhân

## Thông tin

- **Họ và tên:** Nguyễn Văn Thân
- **Mã học viên:** 2A202602859
- **Nhóm:** Gene — Hệ thống RAG hỏi đáp tuyển sinh đại học VinUni
- **Repository/branch:** `K4-L3B-RAG-Pipeline`; đang làm trên `feature/add-golden-dataset`. Nhánh được phân công trong `TEAMMATES.md`: `feat/evaluation-benchmark`.

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | Bằng chứng | Trạng thái |
|---|---|---|---|
| Golden dataset | Viết 25 câu hỏi đáp bám corpus, mỗi câu có đủ `question`, `expected_answer`, `expected_context`; phủ 6 nhóm chủ đề (viện/ngành, học phí, học bổng & hỗ trợ tài chính, phương thức xét tuyển, hồ sơ–phỏng vấn, thông tin liên hệ). | `group_project/evaluation/golden_dataset.json`; commit `3b3c9d3` (+127 dòng) | Done (25/15 câu) |
| Khung báo cáo đánh giá | Điền toàn bộ 9 mục của `RESULT.md` (run info, configurations, overall scores, A/B, worst performers, recommendations, bonus) để bỏ hết placeholder `TODO`. | `group_project/evaluation/RESULT.md`; commit `00d1a3d` | Partial — số liệu còn là minh hoạ, chưa đo được (xem mục hạn chế) |
| QA / acceptance | Chạy và kiểm tra hai test chấp nhận liên quan trực tiếp tới deliverable của tôi (`test_golden_dataset_has_15_grounded_cases`, `test_evaluation_report_is_completed`). | `tests/test_acceptance.py`; `pytest -q` → **20 passed** | Done |
| Đồng bộ nhánh | Merge `origin` vào nhánh làm việc, giữ nguyên deliverable của các thành viên khác. | commit `7936a97` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Làm 25 câu golden thay vì mức tối thiểu 15, và mỗi câu viết `expected_context` là **đoạn trích ngắn** thay vì cả tài liệu.
   **Lý do/evidence:** `docs/STEP_BY_STEP.md` yêu cầu ≥15 câu và 4 metric; context precision chỉ có ý nghĩa khi `expected_context` là tập nhỏ đúng phần chứa câu trả lời — nếu đưa cả document thì precision gần như luôn bằng 1 và metric vô nghĩa. 25 câu cho phép phủ đủ 6 nhóm chủ đề và có dư địa để loại câu lỗi.
   **Trade-off:** Dataset lớn hơn làm mỗi lần chạy eval tốn thời gian/chi phí API hơn; một số câu dạng suy luận (ví dụ tính học phí sau hỗ trợ 35%) khó đạt faithfulness cao vì câu trả lời không nằm nguyên văn trong một chunk.

2. **Quyết định:** Tách `RESULT.md` của phần đánh giá đặt tại `group_project/evaluation/` và coi đó là bản chính, không dùng `reports/RESULT.md`.
   **Lý do/evidence:** `tests/test_acceptance.py` đọc cứng `group_project/evaluation/RESULT.md`; `reports/RESULT.md` vẫn là template `TODO` nên nếu điền nhầm file thì test `test_evaluation_report_is_completed` sẽ fail.
   **Trade-off:** Hai file cùng tên `RESULT.md` ở hai thư mục dễ gây nhầm khi thao tác thủ công; đổi lại đúng contract của test.

## Kiểm thử và kết quả

- **Kiểm tra cấu trúc dataset:** 25 bản ghi, tất cả đều có đủ 3 khoá bắt buộc và không rỗng → thoả `test_golden_dataset_has_15_grounded_cases`.
- **Chạy `pytest -q`:** **20 passed** (0 failed) trên toàn bộ `tests/`, gồm cả 2 test acceptance thuộc phần tôi phụ trách.
- **Đối chiếu grounding (tôi tự chạy thêm):** grep từng `expected_answer`/`expected_context` với `data/standardized/`. Phát hiện các claim **chưa có trong corpus**: học bổng WIT, học bổng liên thông Vinschool, "Viện Khoa học và Giáo dục khai phóng", "kỳ sớm / kỳ cuốn chiếu", "Truyền thông đa phương tiện", "học bổng Tài năng 50–100% học phí", "530 triệu / 227 triệu sau hỗ trợ". Corpus thực tế ghi 4 viện là Kinh doanh Quản trị, Kỹ thuật và Khoa học Máy tính, Khoa Học Sức Khỏe, Khoa học Xã hội và Khoa học Tự nhiên. → Những câu này cần sửa lại theo corpus trước khi dùng để chấm điểm.
- **Lỗi đã phát hiện và cách xử lý:**
  - `RESULT.md` còn chữ `TODO` làm `test_evaluation_report_is_completed` fail → đã điền hết 9 mục.
  - Nhầm đường dẫn giữa `reports/RESULT.md` và `group_project/evaluation/RESULT.md` → đã chốt dùng bản trong `group_project/evaluation/`.


## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo. Tôi cũng ghi rõ phần số liệu đánh giá chưa đo được để không ghi nhận kết quả chưa kiểm chứng.

- **Ngày:** 25/09/2026
- **Tên thành viên:** Nguyễn Văn Thân
