# Story 1.1: Reddit RSS Signal Collector

Status: ready-for-dev

## Story

As a POD Seller,
I want to automatically collect rising and hot post titles from Reddit via RSS,
So that I can identify viral topic ideas without manual browsing.

## Acceptance Criteria

1. **Given** a list of target subreddits and RSS endpoints (rising, hot, top).
2. **When** the Reddit collector is executed.
3. **Then** the script successfully fetches raw titles and metadata.
4. **And** saves unique records into the `signals` table.

## Tasks / Subtasks

- [ ] Repository Setup & Config (AC: 1)
  - [ ] Add subreddit list to `config.yaml` or `.env`.
  - [ ] Define target endpoints (rising.rss, hot.rss, top.rss).
- [ ] Database Schema Prep (AC: 4)
  - [ ] Ensure `signals` table exists with structure: `id`, `source`, `title`, `url`, `external_id`, `created_at`, `raw_data`.
- [ ] RSS Engine Implementation (AC: 2, 3)
  - [ ] Use `feedparser` to parse Reddit RSS feeds.
  - [ ] Implement deduplication based on `external_id` (Reddit permalink/id).
  - [ ] Extract `created_utc` and normalize to `created_at`.
- [ ] Error Handling & Rate Limiting (AC: 3)
  - [ ] Handle 404/429/500 responses gracefully.
  - [ ] Log failed attempts.

## Dev Notes

- **Architecture Pattern**: Use the existing `db/database.py` for SQLite operations.
- **Library**: `feedparser` is recommended for robust RSS handling. Avoid standard `xml.etree` for stability with malformed RSS.
- **Source tree components**: `collectors/reddit.py` (New), `main.py` (Update entry point).
- **Testing**: Manual verification by checking the `signals` table entries after a run.

### Project Structure Notes

- New collector should reside in a `collectors/` directory to maintain modularity.
- Database interaction must use Pydantic models from `models.py` for validation.

### References

- [PRD: signals table definition](file:///C:/Users/doguk/OneDrive/Belgeler/test%20Trend/_bmad-output/planning-artifacts/prd-test-Trend-v2-2026-03-15.md#L340)
- [Epics: Story 1.1 Definition](file:///C:/Users/doguk/OneDrive/Belgeler/test%20Trend/_bmad-output/planning-artifacts/epics.md#L102)

## Dev Agent Record

### Agent Model Used

Antigravity-v1

### Debug Log References

### Completion Notes List

### File List
