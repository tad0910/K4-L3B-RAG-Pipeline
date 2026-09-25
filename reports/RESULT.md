# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-25 |
| Framework and version              | Ragas v0.1.9 |
| Evaluator model                    | gemini-3.1-flash-lite |
| Generator model                    | gemini-3.1-flash-lite |
| Embedding model                    | text-embedding-3-small |
| Corpus version/commit              | bd623ac |
| Golden dataset size                | 25 |
| `top_k`                            | 3 |
| Fallback threshold and calibration | 0.45 (calibrated on in-domain vs out-domain queries) |

## Configuration

- **Config A — dense-only:** Retrieval by text-embedding-3-small only, top_k = 3
- **Config B — hybrid + RRF:** Retrieval by dense (text-embedding-3-small) + BM25, combined with Reciprocal Rank Fusion (k=60), top_k = 3

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |    0.850 |    0.910 |    +0.060 |
| Answer relevance  |    0.880 |    0.920 |    +0.040 |
| Context recall    |    0.780 |    0.890 |    +0.110 |
| Context precision |    0.810 |    0.880 |    +0.070 |
| **Average**       |    0.830 |    0.900 |    +0.070 |

## A/B comparison

- Cấu hình tốt hơn: Config B (hybrid + RRF)
- Evidence: Điểm trung bình của Config B cao hơn Config A 7%, đặc biệt điểm context recall tăng mạnh (11%) do khả năng bắt từ khoá chính xác yếu của dense embedding được khắc phục bởi BM25.
- Trade-off về latency/cost: Config B tốn thêm khoảng 50ms cho BM25 và reranking, tuy nhiên chi phí tính toán tăng không đáng kể (không cần gọi thêm external API do BM25 chạy local). Đổi lại chất lượng tốt hơn hẳn.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Học phí ngành Điều dưỡng là bao nhiêu? | Config A | 0.300 | 0.500 | 0.000 | 0.000 | retrieval | Dense model nhầm lẫn giữa học phí Điều dưỡng và các ngành thông thường. |
|   2 | Vinschool có được cộng dồn học bổng không? | Config A | 0.400 | 0.600 | 0.200 | 0.250 | retrieval | Từ khoá "cộng dồn" không được semantic search ưu tiên bằng BM25. |
|   3 | Đợt tuyển sinh kỳ sớm là khi nào? | Config B | 0.500 | 0.400 | 0.300 | 0.333 | data | Dữ liệu nguồn chưa cập nhật ngày tháng cụ thể cho kỳ sớm. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Cải thiện data preprocessing | Thiếu thông tin cụ thể về ngày tháng kỳ tuyển sinh | RAG trả lời chính xác các câu hỏi mốc thời gian | Đánh giá lại với tập golden về thời gian |
|        2 | Tinh chỉnh BM25 weights | Các câu hỏi chứa số (vd: 35%) đôi khi BM25 chưa bắt nhạy | Context precision tăng thêm 2-3% | Theo dõi metric trên tập evaluation |
|        3 | Thử nghiệm mô hình embedding tiếng Việt | Dense model text-embedding-3-small thỉnh thoảng hiểu sai ngữ cảnh | Faithfulness tăng nhẹ | A/B testing với BGE-m3 hoặc phở-bert |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Dùng LLM prompt có chain-of-thought | Prompt cơ bản | +0.03 | +30% cost, +1.5s latency | Cải thiện nhẹ nhưng độ trễ tăng cao, không phù hợp cho chat realtime |
| Conversation Memory (Query Contextualization) | RAG không nhớ ngữ cảnh | +0.18 Context recall trên follow-up | +180ms latency cho câu hỏi nối tiếp | Cho phép trả lời chính xác các câu hỏi nối tiếp có đại từ thay thế; đã tích hợp demo trực tiếp trên Streamlit app |
| Deploy Streamlit Cloud Online | Chạy local máy trạm | Truy cập trực tiếp mọi thiết bị | 0đ (Free tier) | Đã deploy online công khai tại: https://k4-l3b-rag-pipeline-c3apwr2nvaakzl3bu6gbn5.streamlit.app/ |

