# FSM
## FSM 상태
```
IDLE: 사용자 대기
LISTENING: 사용자 발화 듣는 중
MENU_GUIDE: 메뉴 버튼 안내
OPTION_GUIDE: 옵션 선택 안내
PAYMENT_GUIDE: 결제 버튼 안내
CONFIRM: 주문 완료 확인
ERROR_RECOVERY: 오조작 복구
FAIL_SAFE: 장시간 멈춤, 혼란 발화 시 LLM 보조
```

## 상태전이
```
IDLE → LISTENING → MENU_GUIDE → OPTION_GUIDE → PAYMENT_GUIDE → CONFIRM
                      ↘
                    ERROR_RECOVERY
                          ↘
                        FAIL_SAFE
```

## 상태 전이 표
```
| 상태명            | 설명        | 진입 조건           | 다음 상태                          |
| -------------- | --------- | --------------- | ------------------------------ |
| IDLE           | 사용자 대기    | 시스템 시작, 사용자 없음  | LISTENING                      |
| LISTENING      | 음성 입력 수신  | 사용자 감지, 발화 시작   | MENU_GUIDE                     |
| MENU_GUIDE     | 메뉴 선택 유도  | 메뉴 의도 인식        | OPTION_GUIDE / ERROR_RECOVERY  |
| OPTION_GUIDE   | 옵션 선택 유도  | 메뉴 선택 완료        | PAYMENT_GUIDE / ERROR_RECOVERY |
| PAYMENT_GUIDE  | 결제 버튼 유도  | 옵션 선택 완료        | CONFIRM / ERROR_RECOVERY       |
| CONFIRM        | 주문 완료 확인  | 결제 성공           | IDLE                           |
| ERROR_RECOVERY | 잘못된 상태 복구 | 오조작, 예상 외 화면    | 이전 정상 상태 / FAIL_SAFE           |
| FAIL_SAFE      | LLM 보조 안내 | 3초 이상 멈춤, 혼란 발화 | ERROR_RECOVERY / 정상 상태         |
```

## 마커 ID 
```
00~09 : 시스템 기본 상태
10~19 : 메뉴 선택 상태
20~29 : 옵션 선택 상태
30~39 : 결제 상태
90~99 : 오류 / 복구 상태
```

```
| Marker ID | 상태명            | 의미        |
| --------- | -------------- | --------- |
| 0         | IDLE           | 초기 대기 화면  |
| 1         | LISTENING      | 음성 입력 대기  |
| 10        | MENU_GUIDE     | 메뉴 안내     |
| 20        | OPTION_GUIDE   | 옵션 안내     |
| 30        | PAYMENT_GUIDE  | 결제 안내     |
| 40        | CONFIRM        | 완료 상태     |
| 90        | ERROR_RECOVERY | 복구 유도     |
| 99        | FAIL_SAFE      | LLM 보조 개입 |
```

```python
STATE_MAP = {
    0: "IDLE",
    1: "LISTENING",
    10: "MENU_GUIDE",
    20: "OPTION_GUIDE",
    30: "PAYMENT_GUIDE",
    40: "CONFIRM",
    90: "ERROR_RECOVERY",
    99: "FAIL_SAFE"
}
```

## 버튼 위치 예시
```json
{
  "screen": "menu",
  "buttons": {
    "americano": { "x": 1240, "y": 530 },
    "latte": { "x": 1580, "y": 530 },
    "payment": { "x": 1820, "y": 980 }
  }
}
```

## 상태별 좌표 구조 예시
```json

{
  "MENU_GUIDE": {
    "target_button": "americano",
    "screen": "menu",
    "position": { "x": 1240, "y": 530 }
  },
  "PAYMENT_GUIDE": {
    "target_button": "payment",
    "screen": "checkout",
    "position": { "x": 1820, "y": 980 }
  }
}
```
## 마커 기준 상대 오프셋 데이터 예시
```json
{
  "marker_id": 10,
  "screen": "menu",
  "target_button": "americano",
  "offset_from_marker": {
    "x": 0.032,
    "y": -0.014,
    "z": 0.000
  }
}
```

## 포즈 추정 연동 데이터 예시
```json
{
  "marker_id": 10,
  "state": "MENU_GUIDE",
  "pose": {
    "rvec": [0.21, -0.03, 0.02],
    "tvec": [0.13, 0.04, 0.58]
  },
  "target_button": {
    "name": "americano",
    "ui_position": [1240, 530],
    "offset_from_marker": [0.032, -0.014, 0.000]
  }
}
```