# [Core] 10-bit Variable Status Marker & Part 4 Specification

본 문서는 키오스크 앱과 MR 기기 간의 상태 동기화를 위한 **10-bit 가변형 FSM 프로토콜** 및 4번 파트(키오스크 앱)의 구현 규격을 정의한다.

## 1. Marker Identity: Pure State Bridge
- **Pure State**: 마커 ID는 좌표 데이터를 포함하지 않으며, 오직 '현재 시스템 단계'를 전달하는 브릿지 역할을 수행한다.
- **Entity Key**: 하위 비트는 시각화 파트(Part 3)가 `ui_anchor_map.json`에서 상세 정보를 찾기 위한 참조 키로 활용된다.

## 2. 10-bit Variable Layout
상위 2비트로 페이즈(Phase)를 정의하고, 하위 8비트는 해당 문맥에 맞춰 가변적으로 해석한다.

| Bit Range | Field Name | Width | Description |
| :--- | :--- | :--- | :--- |
| `9:8` | **Phase** | 2 bits | 시스템 대단계 (00, 01, 10, 11) |
| `7:0` | **Variable Payload** | 8 bits | Phase 문맥에 따른 가변 데이터 (Entity ID) |

## 3. Phase Definition (Modular Structure)
- **Phase NULL (0x000)**: 초기 대기 상태 및 진입 가이드 단계.
- **Phase 0 (00)**: 메뉴 및 카테고리 탐색 단계.
- **Phase 1 (01)**: **옵션 선택 세부 단계**. 8비트 전체를 활용하여 다양한 옵션 엔티티를 식별함.
- **Phase 2 (10)**: 결제 수단 및 진행 상태 단계.
- **Phase 3 (11)**: 종료 및 초기화 회귀 단계.

## 4. Part 4 (Kiosk App) Implementation Guidance
4번 파트는 시스템의 '상태 공급자'로서 다음의 인터페이스 원칙을 준수해야 한다.

- **Status Transition**: 화면(UI) 전환 발생 시, 해당 단계에 할당된 10-bit 코드를 즉시 마커 렌더러에 업데이트해야 한다.
- **Marker Specs**: 마커는 화면 하단 지정된 영역(스테이션 카메라 화각 내)에 상시 노출되어야 한다.
- **Decoupling**: 현재 단계에서는 구체적인 코드값 대신 **'ID 변경에 따른 마커 업데이트 모듈'** 구현에 집중한다. 상세 매핑 데이터는 키오스크 확정 후 배포된다.