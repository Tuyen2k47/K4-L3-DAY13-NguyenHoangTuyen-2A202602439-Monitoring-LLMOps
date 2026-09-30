# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Nguyễn Hoàng Tuyển
- **MSSV:** 2A202602439
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/Tuyen2k47/K4-L3-DAY13-NguyenHoangTuyen-2A202602439-Monitoring-LLMOps
- **Commit SHA cuối:** *(Cập nhật sau commit cuối)*
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602439` (Project ID: `cmunk19f6084vad0ck7fwi0a2`)

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 0/100 (chưa có log) | 100/100 | Đạt tuyệt đối: chuẩn JSON schema, có correlation ID, đủ enrichment, không rò rỉ PII. |
| `validate_dashboard.py` | 6/6 panel | 6/6 panel | Hợp lệ toàn bộ 6/6 panel theo dashboard contract `config/dashboard.yaml`. |
| `pytest` | 22 passed | 22 passed | Vượt qua 100% các bài test đơn vị (tracing, adapter v4, prompt, pii, validator). |
| Số traces hợp lệ | 0 | 14 traces | Tự tạo trên project Langfuse cá nhân bằng workload thực tế từ `load_test.py`. |
| Số PII leak | 3 (email, phone, card) | 0 leak | Bộ lọc `scrub_event` và regex khử sạch dữ liệu nhạy cảm trước khi ghi ra đĩa. |
| Latency P95 / TTFT P95 | ~160ms / ~50ms | 164ms / 50ms | Đạt tốt ngưỡng SLO (< 3000ms), thời gian phản hồi token đầu tiên nhanh và ổn định. |
| Retrieval success rate | 100% | 100% | 100% requests tìm thấy context phù hợp trong corpus tài liệu. |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Trong `CorrelationIdMiddleware` (`app/middleware.py`), request trước tiên được xóa context cũ qua `clear_contextvars()`. Middleware trích xuất header `x-request-id` hoặc sinh mới chuỗi duy nhất định dạng `req-<8-hex>` (`req-` + `uuid.uuid4().hex[:8]`). Correlation ID sau đó được gắn vào structlog context qua `bind_contextvars(correlation_id=...)`, lưu trong `request.state.correlation_id`, và trả về client qua header `x-request-id` kèm thời gian xử lý `x-response-time-ms`.
- **Các metadata được ghi vào structured log:** Mỗi log record chứa `ts` (ISO UTC), `level`, `service`, `event`, `correlation_id`, `user_id_hash` (băm SHA-256 an toàn), `session_id`, `feature`, `model`, `env`. Ở sự kiện `response_sent`, bổ sung: `latency_ms`, `ttft_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `quality_score`, `tool_name`, `tool_success`, và `answer_preview` đã scrub.
- **Cách bảo đảm PII được scrub trước khi ghi:** Processor `scrub_event` được đăng ký vào chuỗi processors của structlog ngay trước `JsonlFileProcessor` và `JSONRenderer`. Hàm đệ quy `_scrub_nested` quét qua mọi string, dict, list trong payload/event và áp dụng bộ mẫu regex chuẩn trong `app/pii.py` để thay thế email, số điện thoại Việt Nam, CCCD 12 số, thẻ tín dụng và hộ chiếu thành các thẻ `[REDACTED_...]`.
- **Cách kiểm chứng kết quả:** Chạy `python scripts/validate_logs.py`. Script đọc độc lập toàn bộ `data/logs.jsonl`, quét regex phát hiện PII độc lập, kiểm tra các trường bắt buộc và context enrichment, cho kết quả điểm số 100/100 với 0 lỗi rò rỉ PII.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Project Langfuse cá nhân được cấu hình qua cặp key riêng `LANGFUSE_PUBLIC_KEY` và `LANGFUSE_SECRET_KEY` trong `.env`. Mọi traces sinh ra đều mang tag `["lab", feature, model]` và metadata khớp với `correlation_id` trong file log cục bộ của máy.
- **Cấu trúc root/retrieval/generation observations:** Sử dụng Langfuse Python SDK v4:
  - Root span: `@observe(name="lab-agent-run", as_type="agent")` bọc toàn bộ chu trình xử lý của agent.
  - Child observation 1: `start_as_current_observation(name="retrieval", as_type="retriever")` ghi nhận thời gian và kết quả tìm kiếm ngữ cảnh tài liệu (`doc_count`).
  - Child observation 2: `start_as_current_observation(name="generation", as_type="generation")` liên kết với managed prompt, model `claude-sonnet-4-5`, ghi nhận `usage_details` (input/output/total tokens) và `cost_details`.
- **Cách nối trace với log:** Trường `correlation_id` từ middleware được đưa vào metadata của trace qua `propagate_attributes(metadata={"correlation_id": correlation_id})`. Khi mở một dòng log có vấn đề, chỉ cần tìm trace có metadata `correlation_id` tương ứng trên Langfuse để mở trace waterfall chi tiết.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1, mang label `baseline` và `production`.
- **Version/label candidate:** Version 2, mang label `candidate` và `latest`.
- **Trace ID của mỗi version:**
  - Chạy với label `baseline` (Version 1): Trace ID `570a97b0e475018c3fbe98a644361801`
  - Chạy với label `candidate` (Version 2): Trace ID `9792971e426b10b5117509cf781d75ae`
- **Cách promote và rollback `production`:**
  - **Promote:** Trên Langfuse (hoặc qua SDK), chuyển label `production` sang cho Version 2 $\rightarrow$ Gọi request kiểm thử thành công sử dụng Version 2 (Trace ID: `c4e2a860a093ff0fee94d431368dec1a`).
  - **Rollback:** Khi phát hiện Version 2 có dấu hiệu bất thường, chuyển label `production` quay trở lại Version 1 $\rightarrow$ Gọi request kiểm thử xác nhận hệ thống đã khôi phục Version 1 an toàn (Trace ID: `91a35a73f0512987f7a05aac4f1fdab0`). Toàn bộ quá trình không yêu cầu sửa đổi hay deploy lại source code.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Dựng đủ 6 panel theo `config/dashboard.yaml`:
  1. *Latency percentiles & TTFT (ms):* P50, P95, P99 và TTFT P95 kèm ngưỡng SLO 3000ms.
  2. *Request traffic:* Số lượng request tích lũy và rate/phút (ngưỡng $\ge 1$ req/min).
  3. *Error rate & Retrieval success (%):* Tỷ lệ lỗi ($\le 2\%$) và tỷ lệ thành công của RAG retrieval ($\ge 90\%$).
  4. *Cost over time (USD):* Chi phí tích lũy theo thời gian (ngưỡng $\le \$2.50$).
  5. *Input and output tokens:* Tổng số token in và out (ngưỡng $\le 50,000$ tokens).
  6. *Quality proxy:* Điểm chất lượng trung bình theo heuristic (ngưỡng $\ge 0.75$).
- **SLO và lý do chọn:** Chọn SLO `fast_successful_requests`: $99.5\%$ request thành công và có `latency_ms <= 3000ms` trong cửa sổ 28 ngày. Lý do: Ứng dụng AI Chatbot hỗ trợ người dùng cần đảm bảo tính phản hồi nhanh và chính xác; nếu vượt quá 3s người dùng sẽ cảm thấy chậm trễ và rời bỏ dịch vụ.
- **Cách tính error budget:** SLO $99.5\%$ trong 28 ngày tương ứng với error budget là $0.5\%$. Với quy mô 10,000 requests, ngân sách lỗi cho phép tối đa $10,000 \times 0.5\% = 50$ requests bị lỗi HTTP 500 hoặc có thời gian phản hồi vượt quá 3000ms.
- **Ba alert và runbook tương ứng:**
  1. `HighLatencyP95` (Warning, condition `p95(latency_ms) > 3000ms`, duration `5m`): Cảnh báo khi đuôi latency bị chậm. Runbook: Kiểm tra panel latency, lọc correlation ID chậm trong log, mở trace trên Langfuse để xem nghẽn ở retrieval hay generation.
  2. `HighErrorRate` (Critical, condition `error_rate_pct > 2%`, duration `3m`): Cảnh báo khi tỷ lệ lỗi vượt ngân sách. Runbook: Kiểm tra panel errors, lọc sự kiện `request_failed`, xem exception stack trace, kích hoạt fallback response nếu downstream service gặp sự cố.
  3. `LowRetrievalSuccessRate` (Warning, condition `tool_success_rate_pct < 90%`, duration `5m`): Cảnh báo khi bước truy xuất tài liệu RAG bị lỗi. Runbook: Kiểm tra kết nối Vector Database, chuyển tạm thời sang static fallback corpus để bảo toàn chất lượng câu trả lời.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Khoảng thời gian điều tra:** `2026-09-30 04:35:50Z – 04:36:10Z`
- **Triệu chứng từ metrics:** Dashboard và metric latency tăng đột biến từ ~160ms lên 2678ms (vượt ngưỡng 2000ms của Challenge và tiệm cận ngưỡng cảnh báo SLO 3000ms). Khi chạy tải đồng thời 5 requests (`--concurrency 5`), tổng thời gian hoàn thành vượt trên 10,000ms.
- **Log line và correlation ID liên quan:** Lọc `data/logs.jsonl` tại thời điểm sự cố, phát hiện request `correlation_id=req-be91be73`, session `k4-l3b-challenge-s01`, feature `monitoring` có `latency_ms=2678`.
- **Trace ID và span gây ảnh hưởng:** Mở trace cùng `correlation_id` trên Langfuse (Trace ID: `7d3391ba245d74196786132a7236ee43`). Cây quan sát phân tích chi tiết:
  - Root `day13-agent-request` / `lab-agent-run`: 2.652s
  - Span `retrieval` (RETRIEVER): **2.500s** (chiếm 94.3% toàn bộ thời gian)
  - Span `generation` (GENERATION): **0.151s**
- **Root cause:** Bước truy xuất ngữ cảnh tài liệu (`retrieve()` trong RAG) bị nghẽn (do kịch bản `rag_slow` bị kích hoạt, làm mô phỏng trễ 2.5s khi đọc Vector Store), trong khi bước sinh câu trả lời LLM vẫn hoạt động bình thường (chỉ mất ~150ms).
- **Fix action:** Thực hiện khắc phục tức thời bằng cách gọi API tắt sự cố `/incidents/rag_slow/disable`. Sau khi tắt, độ trễ hệ thống ngay lập tức trở về mức bình thường (152ms - 164ms).
- **Preventive measure:**
  - Kích hoạt alert `HighLatencyP95` để phát hiện suy giảm hiệu năng trong vòng 5 phút.
  - Bổ sung tầng bộ nhớ đệm (Redis Cache) cho các truy vấn embedding/retrieval phổ biến.
  - Cấu hình Circuit Breaker với timeout 1000ms cho bước retrieval: nếu vector store không phản hồi trong 1s, tự động ngắt và trả về static context fallback nhằm bảo vệ trải nghiệm người dùng và ngăn cản cạn kiệt error budget.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Quyết định tách biệt hoàn toàn giữa `retrieval` (retriever) và `generation` (generation) dưới dạng các child observations của Langfuse SDK v4. Quyết định này cho phép cô lập chính xác bước nào là nguyên nhân gốc rễ (Root Cause) trong chuỗi xử lý phức tạp của AI Agent thay vì chỉ nhìn thấy tổng thời gian hộp đen.
- **Một lỗi/blocker đã gặp:** Khi gọi `update_prompt` qua SDK để gán nhãn `latest`, Langfuse API trả về lỗi HTTP 400 do nhãn `latest` được Langfuse tự động quản lý cho phiên bản mới nhất và không được truyền thủ công trong `new_labels`.
- **Cách tìm nguyên nhân và xử lý:** Đọc kỹ thông báo lỗi chi tiết từ Langfuse API (`"Label 'latest' is always assigned to the latest prompt version"`), từ đó điều chỉnh danh sách `new_labels` chỉ chứa `['candidate']` cho version 2 và `['baseline', 'production']` cho version 1.
- **Cách hiểu luồng Metrics → Logs → Traces:**
  - *Metrics* là "đồng hồ đo tốc độ", giúp phát hiện triệu chứng xấu trên diện rộng và khoanh vùng mốc thời gian xảy ra sự cố.
  - *Logs* là "danh bạ chi tiết", giúp định danh chính xác request bị ảnh hưởng thông qua `correlation_id` duy nhất mà không làm lộ dữ liệu nhạy cảm.
  - *Traces* là "kính hiển vi", phóng to vào cấu trúc bên trong của request đó để chỉ mặt điểm nghẽn hoặc span gây lỗi.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Prompt versioning và rollback giúp tách biệt rủi ro cấu hình prompt khỏi việc triển khai code; quản lý token/cost ngăn ngừa rủi ro tài chính do prompt quá dài hoặc vòng lặp sinh câu trả lời; SLO và error budget định lượng cam kết chất lượng dịch vụ với khách hàng.
- **Điều quan trọng nhất đã học:** Kỹ năng xây dựng hệ thống Full Observability cho ứng dụng LLM trong thực tế và quy trình điều tra sự cố chuẩn mực dựa trên bằng chứng dữ liệu thay vì suy đoán cảm tính.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Các metric hiện tại dựa trên log JSONL cục bộ; trong môi trường multi-node thực tế có thể mở rộng tích hợp OpenTelemetry Collector để đẩy dữ liệu trực tiếp về Prometheus/Grafana.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [x] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
