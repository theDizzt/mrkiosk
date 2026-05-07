# [Core] Logic Engine: State Provider & Coordinate Integration

로직 엔진은 상태 마커와 JSON 엔티티 체계를 감독하며, 각 파트 간의 독립적 구현을 지휘한다.

## 1. Decentralized Part Responsibilities
- **Part 1 (Vision)**: ArUco 마커 기반 6DoF Pose 데이터 추출 및 마커 ID의 정수 변환 함수 제공.
- **Part 3 (Visualization)**: 로직 엔진의 상태 ID를 Key로 하여 **내부 JSON 파일**에서 로컬 좌표를 로드하고, 6DoF 행렬을 투영하여 자율 시각화 수행.
- **Part 4 (Kiosk)**: UI 전환에 따른 상태 마커 실시간 업데이트 및 렌더링.
- **Part 5 (Voice)**: 상태 트리거 및 리커버리 상황에 따른 음성 가이드 전담.

## 2. Hierarchical Coordinate Integration
본 시스템은 기기 범용성을 위해 좌표계를 계층적으로 관리한다.
1. **Local Space (JSON)**: 키오스크 기종별 UI 엔티티의 상대 좌표.
2. **World Space (Real World)**: ArUco 6DoF 포즈 데이터를 통해 현실 공간에 고정된 좌표.
- **수식 원칙**: $P_{world} = T_{6DoF} \cdot P_{local}$

## 3. Technology Advantage
- **Network-less Sync**: 물리적 시각 채널을 통한 0.1초 내 확정적 실시간 동기화.
- **Modular Adaptability**: 키오스크 변경 시 JSON 데이터와 ArUco 기준점만 수정하면 되는 범용 로직 구조.