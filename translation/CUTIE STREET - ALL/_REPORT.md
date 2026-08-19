# CUTIE STREET - ALL 가사 번역 리포트

아티스트: **CUTIE STREET**
범위: 전곡 (발매순 오름차순)
포맷: 3줄 블록 (원문 / 한글 음차 / 한국어 의미)
소스: utaten
총 25곡 — 전부 ok

| # | Song | Status |
|---|------|--------|
| 01 | Can't we just be cute_ -Kawaii Dakejya Damedesuka_- | ok |
| 02 | Hello Hello Future | ok |
| 03 | Devoted Cinderella! | ok |
| 04 | Unlock My Heart | ok |
| 05 | daylight | ok |
| 06 | Happy World! | ok |
| 07 | LOVE TRAIN | ok |
| 08 | Haru Flake | ok |
| 09 | The project of the earth-makeup | ok |
| 10 | We can't stop suddenly! | ok |
| 11 | A Little Spoonful | ok |
| 12 | More Berry Summer | ok |
| 13 | Can You Find Our Cuteness_ -Kawaii Sagashite Kuremasuka_- | ok |
| 14 | Song of CUTIE STREET | ok |
| 15 | Chosen Path | ok |
| 16 | Shooting Star | ok |
| 17 | Pri Kyu Kyu | ok |
| 18 | Dreaming Prima Donna | ok |
| 19 | Discommutant! | ok |
| 20 | ナイスだね | ok |
| 21 | I Amai Me Mind | ok |
| 22 | Crush on you | ok |
| 23 | キュートなキューたい | ok |
| 24 | ホメマクリズム | ok |
| 25 | Error404♡ | ok |

## 해결 이력

- **15. Chosen Path** — 본문이 ぷりきゅきゅ(17. Pri Kyu Kyu)의 가사와 동일한 오수록 상태였다. 원곡 제목은 **多元幸福論**(utaten `/lyric/sz25100303/`, 作词 吉田司 / 작곡 吉田司・川村祐寧)으로 확인. 근거: ① utaten 아티스트 페이지의 CUTIE STREET 곡 중 폴더에 대응하는 영문 제목이 없는 유일한 곡, ② 가사 「あの日 あの時 あの場所で 別の道を選んでたら」가 영문 제목 Chosen Path와 직결, ③ 등록일 2025-10-03 이 README 발매일 2025-09-29 과 근접. 본문을 多元幸福論 번역으로 교체하고 크레딧 블록을 추가 → `ok`.
- **19. Discommutant!** — 15번과 마찬가지로 본문이 ぷりきゅきゅ 가사였고 크레딧(`作词 : YUPPA`)까지 ぷりきゅきゅ의 것이었다. 원곡은 **でぃすこみゅーたんと！**(utaten `/lyric/sz26021903/`, 作词·작곡 ナユタン星人). 본문·크레딧을 교체 → `ok`. 15번 수정 때 쓴 완전일치 해시 중복검사로는 잡히지 않았고(17번과 「誰？」/「だぁれ～～～???」 등 몇 줄이 달랐다), 정규화 후 라인 교집합 비율 검사로 재검출했다.
- **크레딧 일괄 보강** — 크레딧 블록이 없던 16곡(01·02·03·05·06·07·08·09·10·11·12·13·14·16·17·18)에 `作词`/`작곡` 추가. 출처는 utaten JSON-LD(14곡), 13·16번은 utaten에 크레딧 데이터가 없어 petitlyrics로 폴백(§8). 편곡 정보는 어느 소스에도 없어 생략. 곡-파일 대응은 제목이 아니라 정규화된 가사 라인 교집합으로 확인(2순위 후보와 명확히 분리).
- **크레딧 표기 통일** — 20·21·22·23번의 `作詞`(번체)를 하우스 스타일 `作词`로 교체(§2, 리포 전역 1400/350). 각 파일에 1회씩만 등장하는 크레딧 줄이라 가사 본문에는 영향 없음. 이제 폴더 전체 25곡이 `作词`.
- **3줄 블록 미완성 보정** — 14번의 단독 원문 줄 3개(`I LOVE YOU～！！`, `CU CU CU CU CUTE！`, `KAWAII MAKER！`)와 17번의 `3, 2, 1`에 음차·의미 줄을 추가. 14번 맨 앞의 `**Song of CUTIE STREET — CUTIE STREET**` 는 제목+아티스트가 중복된 헤더 줄이라 번역하지 않고 삭제. 추가로 14번 `大優勝！プレミアム！I LOVE YOU～！！` 블록은 음차·의미 줄에서 `I LOVE YOU～！！` 가 누락돼 있어 같이 보정했다.
- **04. Unlock My Heart** — 원곡 제목은 **解**(utaten `/lyric/qa41058021/`). 作词·작곡 YUNOSY, 첫 줄 「どうにか上手く言葉にしたいのに」가 파일 내용과 일치. 이미 수록된 곡이므로 별도 추가 없음.
