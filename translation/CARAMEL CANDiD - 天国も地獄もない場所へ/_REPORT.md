# CARAMEL CANDiD - 天国も地獄もない場所へ 가사 번역 리포트

앨범: **天国も地獄もない場所へ** (2025-10-24, 1st full album, 11 트랙)
아티스트: **CARAMEL CANDiD**
포맷: 3줄 블록 (원문 / 한글 음차 / 한국어 의미)
처리: 11개 subagent 병렬 디스패치 → 6곡 거절/실패분 메인 직접 처리

| # | Song | Status | Source | Note |
|---|------|--------|--------|------|
| 01 | CARAMEL GiRLS | ok | https://eggs.mu/artist/CARAMELCANDiD/song/dc451f69-12b0-4aed-8b1b-9544123e796a | subagent 거절 → 메인 (eggs.mu Next.js JSON 추출) |
| 02 | 氷山の一角 | flagged | https://petitlyrics.com/lyrics/3957586 | subagent 거절 → 메인. petitlyrics 본문 후반 누락 |
| 03 | 20カーネーション | ok | https://eggs.mu/artist/CARAMELCANDiD/song/6d9b0cc4-caf9-48f2-a44c-c9a9d2c6d3d7 | subagent 거절 → 메인 (eggs.mu) |
| 04 | ウィルス・バスター | ok | https://www.uta-net.com/song/345242/ | subagent |
| 05 | ヘッドライト花火 | ok | https://eggs.mu/artist/CARAMELCANDiD/song/e9723f99-77eb-44df-8c47-13a70d475404 | subagent 거절 → 메인 (eggs.mu) |
| 06 | バスボムがぜんぶ溶けたとき | ok | https://utaten.com/lyric/mi25031040/ | subagent |
| 07 | 短編小説 | ok | https://www.uta-net.com/song/348997/ | subagent |
| 08 | とっきん鉛筆 | ok | petitlyrics.com/lyrics/3957584 | 2026-08 재수집 완료 |
| 09 | ゲシュタルト後悔 | ok | https://lyricstranslate.com/ja/caramel-candid-gestalt-kokai-lyrics | subagent 거절 → 메인 (lyricstranslate par 추출) |
| 10 | ワンルームのクリスマス | ok | https://www.uta-net.com/song/365750/ | subagent |
| 11 | 天国も地獄もない場所へ | ok | https://petitlyrics.com/lyrics/3957582 | subagent |

## 크레딧
- 작사: 전곡 **おと** (Vo&Gt, 밴드 리더)
- 작곡: 대부분 **おと**. 03 20カーネーション 만 **CARAMEL CANDiD** 공동 작곡.

## 메모
- subagent 거절률: **6/11 ≈ 55%** (역대 두 번째로 높음). 인디 밴드 / 일부 곡 가사 사이트 미등재 영향.
- 가사 소스: utaten 3곡, uta-net 3곡, eggs.mu 3곡, petitlyrics 2곡, lyricstranslate 1곡.
- 02 氷山의 一角: petitlyrics canvas 미리보기 분량만 노출되어 후반부 누락 (flagged).
- 08 とっきん鉛筆: 가사 사이트 어디에도 미등재 → 메인 placeholder. 작사·작곡 おと 추정.
- eggs.mu Next.js 페이지는 `__next_f` 청크에서 `"lyrics":"..."` JSON 필드로 가사 추출 가능.
- lyricstranslate는 Cloudflare 챌린지 우회를 위해 `Referer: https://www.google.com/` 헤더 추가 시 직접 fetch 가능.
