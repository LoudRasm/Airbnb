    if not allow_api:
        missing = [row['review_id'] for row in selected
                   if _cache_key(row['review_id'], comment_sha256(row.get('comments', '')), model, p_hash) not in cache]
        if missing:
            raise RuntimeError(f'LLM cache thiếu {len(missing)}/{len(selected)} review đúng ID/text/model/prompt. '
                               'Chạy scripts/generate_llm_cache.py trước khi nộp; pipeline không gọi API.')
