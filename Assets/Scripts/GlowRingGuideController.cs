using UnityEngine;

public class GlowRingGuideController : MonoBehaviour
{
    [Header("Data Source Settings")]
    public bool useUdp = true;
    public UdpRuntimeStateReceiver udpReceiver;
    public RuntimeStateReader runtimeStateReader;

    [Header("Target Object")]
    public Transform glowRing;

    [Header("Adjustment Settings")]
    [Tooltip("파이썬 미터 좌표 축 연산 배율 (기본값 1.0)")]
    public float positionScale = 1.0f;
    [Tooltip("링 크기 스케일 배율 (기본값 1.0)")]
    public float scaleFactor = 1.0f;

    private void Update()
    {
        Vector3 targetPosition = Vector3.zero;
        Vector2 targetSize = Vector2.one;
        bool hasData = false;

        // 1. UDP 또는 파일 리더를 통해 실시간 파이썬 마커 데이터 동기화
        if (useUdp)
        {
            if (udpReceiver != null && udpReceiver.latestState != null && udpReceiver.latestState.valid)
            {
                var target = udpReceiver.latestState.fsm.target;
                if (target != null && target.world_position != null)
                {
                    // 파이썬 카메라의 원본 3D 위치 값을 오차 없이 1:1 대입
                    targetPosition = new Vector3(
                        target.world_position.x,
                        target.world_position.y,
                        target.world_position.z
                    );

                    // 팀원분의 UdpRuntimeStateReceiver.WorldSize 내부 변수명 (w, h) 완벽 호환 조치
                    if (target.world_size != null)
                    {
                        targetSize = new Vector2(target.world_size.w, target.world_size.h);
                    }
                    hasData = true;
                }
            }
        }
        else
        {
            if (runtimeStateReader != null && runtimeStateReader.CurrentState != null && runtimeStateReader.HasTargetRect())
            {
                targetPosition = runtimeStateReader.GetTargetWorldPosition();
                targetSize = runtimeStateReader.GetTargetWorldSize();
                hasData = true;
            }
        }

        // 2. 오브젝트 트랜스폼 연산 및 렌더링 스위칭
        if (glowRing != null)
        {
            if (hasData)
            {
                glowRing.gameObject.SetActive(true);
                
                // 파이썬 주소 축은 내 눈(카메라) 중심이므로 로컬 좌표계로 완벽 투사
                glowRing.localPosition = targetPosition * positionScale;

                // 크기도 파이썬 원본 스케일 그대로 대입
                glowRing.localScale = new Vector3(
                    targetSize.x * scaleFactor,
                    targetSize.y * scaleFactor,
                    1.0f
                );
            }
            else
            {
                // 실시간 트래킹 데이터 단절 시 잔상 방지를 위해 비활성화
                glowRing.gameObject.SetActive(false);
            }
        }
    }
}