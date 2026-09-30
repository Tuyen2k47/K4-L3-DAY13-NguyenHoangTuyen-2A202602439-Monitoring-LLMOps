# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường (retrieval vs generation).
- Mitigation tạm thời: Rollback prompt nếu do prompt dài/chậm, kiểm tra vector database, tắt scenario lỗi hoặc scale tài nguyên.
- Owner: `student-2A202602439`

## Alert 2

- Tên: `HighErrorRate`
- Severity: `critical`
- Duration: `3m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: error rate của service API (`request_failed` / `request_received`)
- Điều kiện và thời gian duy trì: `error_rate_pct > 2%` trong 3 phút
- Ảnh hưởng tới người dùng: người dùng nhận lỗi HTTP 500 hoặc không nhận được câu trả lời từ chatbot.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard Errors để xem tỷ lệ lỗi và breakdown theo `error_type`.
  2. Lọc `data/logs.jsonl` lấy sự kiện `request_failed` gần nhất, trích xuất `correlation_id` và error detail.
  3. Mở trace trên Langfuse để xem exception stack trace ở span con nào.
- Mitigation tạm thời: Nếu do downstream service/tool fail, kích hoạt fallback response; khởi động lại worker hoặc rollback version triển khai gần nhất.
- Owner: `student-2A202602439`

## Alert 3

- Tên: `LowRetrievalSuccessRate`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: tỷ lệ thành công của retrieval tool (`tool_success == true` / `tool_success != null`)
- Điều kiện và thời gian duy trì: `tool_success_rate_pct < 90%` trong 5 phút
- Ảnh hưởng tới người dùng: chatbot thiếu thông tin context dẫn đến câu trả lời hallucinate hoặc chất lượng kém.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel Errors/Retrieval để kiểm tra mức giảm tỷ lệ thành công của `tool_name="retrieval"`.
  2. Lọc log sự kiện có `tool_success=False`, kiểm tra `error_type` (ví dụ `RuntimeError: Vector store timeout`).
  3. Mở trace tương ứng trên Langfuse để kiểm tra span `retrieval`.
- Mitigation tạm thời: Chuyển sang fallback corpus tĩnh hoặc cấu hình retrieval cache trong khi khôi phục vector store.
- Owner: `student-2A202602439`
