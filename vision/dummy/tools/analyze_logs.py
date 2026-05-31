import json
import math
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict


# 설정값

# log.jsonl 위치
# 루트에서 실행할 경우: python tools/analyze_logs.py
LOG_FILE = Path("log.jsonl")

# 좌표가 이 거리 이상 갑자기 바뀌면 "튐"으로 판단
POSITION_JUMP_THRESHOLD = 0.08  # meter


# 유틸 함수
def parse_time(timestamp: str):
    # ISO 형식 timestamp 문자열을 datetime 객체로 변환

    try:
        return datetime.fromisoformat(timestamp)
    except Exception:
        return None


def get_position_from_log(log: dict):
    # 로그에서 좌표를 추출한다.
    # 우선순위
    # 1) payload.world_position
    # 2) tvec

    payload = log.get("payload", {})

    world_position = payload.get("world_position")
    if world_position:
        return {
            "x": float(world_position.get("x", 0.0)),
            "y": float(world_position.get("y", 0.0)),
            "z": float(world_position.get("z", 0.0)),
        }

    tvec = log.get("tvec")
    if tvec and len(tvec) >= 3:
        return {
            "x": float(tvec[0]),
            "y": float(tvec[1]),
            "z": float(tvec[2]),
        }

    return None


def distance_3d(a: dict, b: dict):
    # 두 3D 좌표 사이 거리 계산

    return math.sqrt(
        (a["x"] - b["x"]) ** 2 +
        (a["y"] - b["y"]) ** 2 +
        (a["z"] - b["z"]) ** 2
    )


def load_logs(log_file: Path):
    # jsonl 로그 파일을 한 줄씩 읽어서 리스트로 반환

    if not log_file.exists():
        print(f"[ERROR] Log file not found: {log_file}")
        return []

    logs = []

    with open(log_file, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"[WARN] Invalid JSON at line {line_number}")

    return logs


# 분석 함수
def analyze_logs(logs):
    # 로그 리스트를 분석하여 통계 결과를 만든다.

    if not logs:
        return None

    total_events = len(logs)

    state_counter = Counter()
    marker_counter = Counter()
    event_counter = Counter()

    error_recovery_count = 0
    fail_safe_count = 0

    state_enter_times = defaultdict(list)

    position_jump_count = 0
    position_jump_details = []

    previous_log = None
    previous_position = None
    previous_time = None
    previous_state = None

    state_durations = []

    for log in logs:
        state = log.get("state", "UNKNOWN")
        marker_id = log.get("marker_id", "UNKNOWN")
        event = log.get("event", "UNKNOWN")
        timestamp = log.get("timestamp")

        time_obj = parse_time(timestamp) if timestamp else None
        position = get_position_from_log(log)

        state_counter[state] += 1
        marker_counter[marker_id] += 1
        event_counter[event] += 1

        if state == "ERROR_RECOVERY":
            error_recovery_count += 1

        if state == "FAIL_SAFE":
            fail_safe_count += 1

        if time_obj is not None:
            state_enter_times[state].append(time_obj)

        # 상태 유지 시간 계산
        if previous_time is not None and time_obj is not None and previous_state is not None:
            duration = (time_obj - previous_time).total_seconds()

            if duration >= 0:
                state_durations.append({
                    "from_state": previous_state,
                    "to_state": state,
                    "duration": duration
                })

        # 좌표 튐 감지
        if previous_position is not None and position is not None:
            dist = distance_3d(previous_position, position)

            if dist > POSITION_JUMP_THRESHOLD:
                position_jump_count += 1
                position_jump_details.append({
                    "from_state": previous_state,
                    "to_state": state,
                    "distance": dist,
                    "timestamp": timestamp
                })

        previous_log = log
        previous_position = position
        previous_time = time_obj
        previous_state = state

    average_state_duration = 0.0

    if state_durations:
        average_state_duration = sum(item["duration"] for item in state_durations) / len(state_durations)

    most_common_state = state_counter.most_common(1)[0] if state_counter else ("NONE", 0)

    recovery_rate = error_recovery_count / total_events * 100
    fail_safe_rate = fail_safe_count / total_events * 100

    result = {
        "total_events": total_events,
        "state_counter": state_counter,
        "marker_counter": marker_counter,
        "event_counter": event_counter,
        "error_recovery_count": error_recovery_count,
        "fail_safe_count": fail_safe_count,
        "recovery_rate": recovery_rate,
        "fail_safe_rate": fail_safe_rate,
        "average_state_duration": average_state_duration,
        "most_common_state": most_common_state,
        "position_jump_count": position_jump_count,
        "position_jump_details": position_jump_details,
        "state_durations": state_durations
    }

    return result


# 출력 함수
def print_report(result):
    # 분석 결과를 콘솔에 보기 좋게 출력

    if result is None:
        print("[INFO] No logs to analyze.")
        return

    print("\n" + "=" * 60)
    print("MR Kiosk Runtime Log Analysis Report")
    print("=" * 60)

    print(f"\nTotal events: {result['total_events']}")

    print("\n[State Counts]")
    for state, count in result["state_counter"].most_common():
        print(f"- {state}: {count}")

    print("\n[Marker ID Counts]")
    for marker_id, count in result["marker_counter"].most_common():
        print(f"- {marker_id}: {count}")

    print("\n[Event Counts]")
    for event, count in result["event_counter"].most_common():
        print(f"- {event}: {count}")

    print("\n[Recovery / Fail-safe]")
    print(f"- ERROR_RECOVERY count: {result['error_recovery_count']}")
    print(f"- ERROR_RECOVERY rate: {result['recovery_rate']:.2f}%")
    print(f"- FAIL_SAFE count: {result['fail_safe_count']}")
    print(f"- FAIL_SAFE rate: {result['fail_safe_rate']:.2f}%")

    print("\n[State Duration]")
    print(f"- Average state transition interval: {result['average_state_duration']:.3f} sec")

    state_name, state_count = result["most_common_state"]
    print(f"- Most frequent state: {state_name} ({state_count})")

    print("\n[Position Stability]")
    print(f"- Position jump threshold: {POSITION_JUMP_THRESHOLD} m")
    print(f"- Position jump count: {result['position_jump_count']}")

    if result["position_jump_details"]:
        print("\n[Position Jump Details]")
        for item in result["position_jump_details"][:10]:
            print(
                f"- {item['timestamp']} | "
                f"{item['from_state']} -> {item['to_state']} | "
                f"jump={item['distance']:.3f} m"
            )

        if len(result["position_jump_details"]) > 10:
            print(f"... and {len(result['position_jump_details']) - 10} more")

    print("\n" + "=" * 60)


def save_report_json(result, output_file: Path):
    # 분석 결과를 JSON 파일로 저장
    # Counter는 dict로 변환해야 저장 가능

    if result is None:
        return

    serializable_result = {
        "total_events": result["total_events"],
        "state_counter": dict(result["state_counter"]),
        "marker_counter": {str(k): v for k, v in result["marker_counter"].items()},
        "event_counter": dict(result["event_counter"]),
        "error_recovery_count": result["error_recovery_count"],
        "fail_safe_count": result["fail_safe_count"],
        "recovery_rate": result["recovery_rate"],
        "fail_safe_rate": result["fail_safe_rate"],
        "average_state_duration": result["average_state_duration"],
        "most_common_state": {
            "state": result["most_common_state"][0],
            "count": result["most_common_state"][1]
        },
        "position_jump_count": result["position_jump_count"],
        "position_jump_details": result["position_jump_details"]
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable_result, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVE] Analysis report saved: {output_file}")


# Main
def main():
    logs = load_logs(LOG_FILE)
    result = analyze_logs(logs)

    print_report(result)

    output_file = Path("analysis_report.json")
    save_report_json(result, output_file)


if __name__ == "__main__":
    main()
