# PompadollS - PompadollS 가사 번역 리포트

앨범: **PompadollS** (2025-12-17, 1st full album, 14 트랙) + 이후 싱글 2곡 (15·16)
아티스트: **PompadollS**
포맷: 3줄 블록 (원문 / 한글 음차 / 한국어 의미)
처리: 14개 subagent 병렬 디스패치 → 6곡 거절/실패분 메인 직접 처리

| # | Song | Status | Source | Note |
|---|------|--------|--------|------|
| 01 | 悪食 | ok | https://utaten.com/lyric/mi25062626/ | subagent |
| 02 | スポットライト・ジャンキー | flagged | https://s.awa.fm/track/6f6902a425734c056d78 | subagent. 「イチイが咲かずに」 [?] |
| 03 | ホワイトジャーニー | ok | https://petitlyrics.com/lyrics/4016473 | subagent (petitlyrics) |
| 04 | 海底孤城 | ok | https://utaten.com/lyric/mi25062619/ | subagent |
| 05 | ラブソング | ok | https://utaten.com/lyric/mi25062620/ | subagent 거절 → 메인 |
| 06 | 日の東、月の西 | ok | https://utaten.com/lyric/mi25062625/ | subagent 거절 → 메인 |
| 07 | ねむり姫 | ok | petitlyrics.com/lyrics/4016471 | 2026-08 재수집 완료 |
| 08 | 命知ラズ | ok | petitlyrics.com/lyrics/4016467 | 2026-08 재수집 완료 |
| 09 | Vanished Vanity | ok | https://petitlyrics.com/lyrics/4016472 | subagent |
| 10 | 怪物 | ok | https://utaten.com/lyric/mi25062624/ | subagent |
| 11 | ネズミの花嫁 | flagged | https://petitlyrics.com/lyrics/4016476 | subagent 거절 → 메인. petitlyrics 본문이 중간에 끊김 → 가사 일부만 번역 |
| 12 | ロールシャッハの数奇な夢 | ok | https://utaten.com/lyric/mi25062617/ | subagent |
| 13 | ヒューマンエラー | flagged | https://petitlyrics.com/lyrics/4016474 | subagent 거절 → 메인. petitlyrics 본문 중간 끊김 → 가사 일부만 번역 |
| 14 | 魔法のランプ | ok | https://www.uta5.com/kasi/115874 | subagent |
| 15 | リトルワールド | ok | (추가 수집) | 2026-04-14 싱글 |
| 16 | ヒグレチガイ | ok | (추가 수집) | 2026-06-09 싱글 |

## 크레딧
전곡 작사·작곡: **五十嵐五十** (Vo/Gt, 밴드 리더)

## 메모
- subagent 거절률: **6/14 ≈ 43%** (Laugh 38% < PompadollS 43% < Completeness 57%). 거절 패턴 유지.
- 가사 사이트 분포: utaten 5곡, petitlyrics 4곡, uta5 1곡, awa 1곡. 일부 곡은 정식 가사 미공개 (07, 08).
- petitlyrics canvas 태그는 HTML entity 인코딩된 텍스트 포함 — 직접 디코드 가능. 단 일부 곡은 미리보기 분량만 노출되어 가사 후반부 누락 (11, 13).
- 07 ねむり姫, 08 命知ラズ 는 미발견. 신곡으로 공식 가사 사이트 등록 전인 듯.
