# [Core] Runtime Flow: Visual Bridge & Recovery

본 시스템은 네트워크 없이 시각적 마커(10-bit)로 상태를 동기화하며, ArUco 6DoF 정합과 JSON 엔티티 매핑을 통해 구동된다.

## 1. Operational Sequence
1. **Idle Stage (NULL / 0x000)**: STT 대기. 메뉴 확정 시 로직 엔진이 가이드 활성화 신호 전송.
2. **First Guide**: 3번 파트가 JSON에서 '주문하기' 엔티티의 로컬 좌표를 로드하고, 6DoF 정합을 통해 현실 공간에 가이드를 투사한다. (5번 파트 음성 동기화)
3. **Activation**: 4번 파트가 화면 전환에 맞춰 마커 ID를 활성화하면, 1번 파트가 이를 인식하여 시스템에 공유한다.
4. **Variable Tracking**: 3번 파트는 수신된 ID를 Key로 삼아 JSON 파일에서 실시간으로 좌표를 조회하여 자율 시각화를 수행한다.

## 2. Deterministic Recovery (AR + Voice)
경로 이탈(`id ∉ Route[]`) 감지 시 수행되는 복합 복구 로직:
- **Detection**: 로직 엔진이 수신된 ID가 설계된 시퀀스 외의 값임을 판별.
- **Action**: 3번 파트는 JSON 내 **'Back_Button' 엔티티**의 로컬 좌표를 즉시 로드하여 AR 가이드를 투사하고, 5번 파트는 복구 음성 안내를 수행한다.
- **Resumption**: 정상 궤도 ID가 재인식될 때까지 리커버리 상태를 유지한다.