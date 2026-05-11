# [Architecture Spec] 10-bit FSM 기반 혼합현실(MR) 키오스크 가이드 시스템

## 목차
1. [전체 인터랙션 데이터 흐름 (Data Flow)](#1-전체-인터랙션-데이터-흐름-data-flow)
2. [이원화 마커 아키텍처 (Dual-Marker Architecture)](#2-이원화-마커-아키텍처-dual-marker-architecture)
3. [10-bit 상태코드 프로토콜 명세 (State Code Protocol)](#3-10-bit-상태코드-프로토콜-명세-state-code-protocol)
4. [엔진 핵심 로직 및 라우팅 (Core Logic & Routing)](#4-엔진-핵심-로직-및-라우팅-core-logic--routing)
5. [예외 처리 및 자가 복구 시나리오 (Exception & Self-Healing)](#5-예외-처리-및-자가-복구-시나리오-exception--self-healing)

---

## 1. 전체 인터랙션 데이터 흐름 (Data Flow)

네트워크 통신 없이 시각적 매체(카메라)만으로 상태를 100% 동기화하는 온디바이스(On-device) 인터랙션 사이클입니다.

| 단계 | 담당 파트 | 설명 |
| :---: | :---: | :--- |
| **① 경로 주입** | Controller | Meta Quest 3 컨트롤러 입력으로 타겟 메뉴의 `[Phase + Entity]` 목표 배열 생성 및 엔진 주입 (STT 모킹) |
| **② 상태 노출** | Part 4 (UI) | 사용자의 터치 또는 화면 전환 시, 키오스크 하단에 현재 상태를 나타내는 10-bit 마커 렌더링 |
| **③ 마커 인식** | Part 1 (Vision) | HMD 카메라가 10-bit 마커를 프레임 단위로 인식, 노이즈 필터링 후 정수형 상태코드로 엔진에 전달 |
| **④ 상태 해석** | 엔진 (Logic) | 비트 마스킹을 통해 수신된 상태코드에서 현재 Phase와 Entity를 $O(1)$ 속도로 분리 및 확정 |
| **⑤ 검증/산출** | 엔진 (Logic) | 주입된 목표 배열과 **[현재 Phase + Entity]**를 비교하여, 다음 타겟의 JSON 로컬 좌표 및 TTS 산출 |
| **⑥ 3D 렌더링** | Part 3 (AR) | 반환된 로컬 좌표를 화면 밖 ArUco 마커의 6DoF 행렬(`T_6DoF`)에 투영하여 주황색 가이드 링 표출 |

```mermaid
sequenceDiagram
    participant C as Controller (Input)
    participant K as Part 4 (Kiosk UI)
    participant V as Part 1 (Vision)
    participant E as Logic Engine (FSM)
    participant AR as Part 3 (AR Guide)

    C->>E: 목표 경로 배열 주입 (PhaseRoute Map)
    
    loop Deterministic Navigation
        K->>V: 10-bit 상태코드 물리적 노출
        V->>E: 정제된 State Code (Int) 전달
        
        rect rgb(240, 240, 240)
        Note over E: [FSM 동기화 판정]
        E->>E: current(P+E) == target(P+E) ?
        end

        E->>AR: 타겟 2D 픽셀 좌표 & TTS 텍스트 리턴
        AR->>AR: ArUco 6DoF 공간 정합 및 가이드 투사
    end

## 2. 이원화 마커 아키텍처 (Dual-Marker Architecture)

혼합현실 공간 렌더링의 안정성과 논리적 상태 전이의 정확성을 확보하기 위해 두 가지 역할을 완전히 디커플링(Decoupling)합니다.

| 분류 | 마커 유형 | 물리적 위치 | 핵심 역할 | 공학적 도입 사유 |
| :--- | :---: | :---: | :---: | :--- |
| **Tracking Anchor** | **ArUco 마커** | 키오스크 베젤 (외부) | 3차원 공간 6DoF 좌표 | 화면(LCD) 전환 및 빛 반사에 독립적인 물리적 앵커 확보. AR 객체가 화면에 고정되게 하여 미끄러짐(Swimming) 방지. |
| **State Bridge** | **10-bit 마커** | 키오스크 화면 (내부) | 논리적 FSM 상태 전이 | API 지연 없이 0.1초 내 즉각적인 상태 동기화. 오직 화면의 현재 Phase와 Entity 정보만 전달. |

---

## 3. 10-bit 상태코드 프로토콜 명세 (State Code Protocol)

### 3.1 비트 레이아웃 (Bit Layout)
상위 2비트로 시스템의 진행 대단계(Phase)를 식별하고, 하위 8비트로 해당 단계 내의 구체적인 UI 요소(Entity)를 식별합니다.

| 비트 범위 | 필드명 (Field) | 비트 폭 (Width) | 데이터 설명 |
| :---: | :--- | :---: | :--- |
| `[9:8]` | **Phase** | 2 bits | 시스템 대단계 (00, 01, 10, 11) |
| `[7:0]` | **Entity** | 8 bits | Phase 내부의 구체적인 옵션, 메뉴, 버튼 ID |

### 3.2 페이즈 및 상태 정의 (Phase Dictionary)
| 상태 코드 | Phase 구분 | 설명 및 화면 상태 |
| :--- | :--- | :--- |
| `00x0000` | **Idle / Init** | 시스템 진입 전 대기 상태 (초기화) |
| `00 (0x00)` | **Phase 1** | **메뉴 선택 단계** (아메리카노, 카페라떼 등 카테고리/상품 선택) |
| `01 (0x01)` | **Phase 2** | **옵션 선택 단계** (수량 증감, 온도 변경, 샷 추가 등) |
| `10 (0x02)` | **Phase 3** | **결제 수단 선택** (신용카드, 현금, 간편결제 선택 화면) |
| `11 (0x03)` | **Phase 4** | **종료 및 회귀** (결제 완료 및 영수증 출력, 초기화 트리거) |

---

## 4. 엔진 핵심 로직 및 라우팅 (Core Logic & Routing)

로직 엔진은 시스템 내부에 가상의 인덱스를 저장하지 않는 무상태(Stateless) 결정론적 제어기입니다. 

### 4.1 상태 동기화 판정식 (Lock-step Condition)
가이드를 다음 단계로 전이시키기 위한 조건은 **Phase와 Entity의 동시 일치**입니다.

1. **정상 전이 (Success)**: `(currentPhase == targetPhase) && (currentEntity == targetEntity)`
   * 사용자가 정답 버튼을 정확히 터치하여 화면 상태가 변경됨을 의미.
   * 엔진은 즉각적으로 다음 페이즈의 타겟 좌표를 JSON에서 로드하여 리턴.
2. **상태 유지 (On-track)**: `(currentPhase == targetPhase) && (currentEntity != targetEntity)`
   * 사용자가 아직 정답 버튼을 누르기 전인 상태.
   * 타겟 버튼을 누르도록 현재 타겟의 가이드 좌표와 링 이펙트를 유지함.

---

## 5. 예외 처리 및 자가 복구 시나리오 (Exception & Self-Healing)

사용자 오조작 및 센서 노이즈로 인한 시스템 데드락을 방지하기 위한 안전장치입니다. 외부 API(LLM 등)에 의존하지 않고 수학적 집합 연산으로 통제합니다.

### 5.1 경로 이탈 판별 (Phase Mismatch)
* **트리거:** 인식된 마커의 Phase가 사전에 주입된 목표 경로 배열(`Target Map`) 내에 존재하지 않음.
* **로직:** 사용자가 엉뚱한 메뉴를 누르거나 뒤로가기를 잘못 눌러 시스템이 예상치 못한 화면에 진입했음을 확정.

### 5.2 자가 복구 시퀀스 (Recovery Handling)
1. **Back Tracking:** `GuideRepository`(JSON)에서 범용 `Back_Button`(뒤로가기)의 로컬 좌표를 강제로 호출.
2. **음성 개입:** Part 5(Voice)를 트리거하여 "이전 화면으로 돌아가주세요" TTS를 5초 간격으로 반복 송출.
3. **루프 복귀:** 사용자가 뒤로가기를 눌러 정상 Phase로 진입하는 즉시 원래의 가이드 내비게이션 재개.
4. **Hard Reset:** 일정 시간/횟수 이상 복구가 지연되거나 물리적 인식 불가 상태 시, 컨트롤러를 통해 시스템을 강제 초기화(`00x0000`)하고 0단계로 회귀.

### 5.3 엔지니어링 설계 결단 (Trade-offs)
* **LLM 의도 분석 배제:** 예외 발생 시 LLM을 호출하여 동적 경로를 탐색하려던 기획을 파기함. MR 렌더링에 필요한 0.1초 미만의 지연율을 네트워크 API가 보장할 수 없으며, 상태코드 기반의 수학적 복귀 로직이 시스템 정합성에 더 부합함.
* **STT 컨트롤러 대체:** 프로토타입 시연 시 발생할 수 있는 소음 환경에서의 음성 인식 실패 리스크를 통제하기 위해 Meta Quest 3의 물리 버튼(`OVRInput`)으로 대체함. 입력 모듈이 교체되더라도 미들웨어 코어의 변경이 없음을 증명하는 아키텍처적 유연성을 내포함.