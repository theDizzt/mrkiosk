// Assets/Scripts/GlowRingGuideController.cs
using UnityEngine;

public class GlowRingGuideController : MonoBehaviour
{
    [Header("References")]
    public RuntimeStateReader runtimeStateReader;
    public UdpRuntimeStateReceiver udpReceiver;
    public Transform glowRing;

    [Header("Input Mode")]
    public bool useUdp = false;

    [Header("Movement")]
    public float moveSpeed = 6.0f;
    public float scaleFactor = 1.2f;

    [Header("Colors")]
    public Color normalColor = new Color(1.0f, 0.373f, 0.082f); // #FF5F15
    public Color recoveryColor = Color.red;

    private Renderer ringRenderer;

    private void Start()
    {
        if (glowRing != null)
        {
            ringRenderer = glowRing.GetComponent<Renderer>();
        }
    }

    private void Update()
    {
        if (glowRing == null)
        {
            return;
        }

        Vector3 targetPosition;
        Vector2 targetSize;
        bool recovery;

<<<<<<< Updated upstream
        if (useUdp)
=======
        // 1. UDP 또는 파일 리더를 통해 실시간 파이썬 마커 데이터 동기화
if (useUdp)
>>>>>>> Stashed changes
        {
            if (
                udpReceiver == null ||
                udpReceiver.latestState == null ||
                udpReceiver.latestState.fsm == null ||
                udpReceiver.latestState.fsm.target == null ||
                udpReceiver.latestState.fsm.target.world_position == null ||
                udpReceiver.latestState.fsm.target.world_size == null
            )
            {
<<<<<<< Updated upstream
                return;
=======
                var fsm = udpReceiver.latestState.fsm;
                if (fsm != null)
                {
                    // 파이썬 비전 엔진이 인식한 실시간 마커 ID 판독
                    int currentMarkerId = fsm.detected_state_id;

                    // 🎯 오퍼레이터 실측 기반: 우리 실험실의 완벽한 2번째 정답 축 베이스 (Z: 1.93m 보정)
                    float baseX = -0.001f; 
                    float baseY = -0.468f;  
                    float baseZ = 1.930f;  

                    // 마커 번호 변경에 맞춰 유니티 가상 공간 상에서 원의 위치를 완벽하게 강제 텔레포트
                    switch (currentMarkerId)
                    {
                        // 1. 메인 홈 화면 (0번 마커) ➔ 화면 정중앙 배치
                        case 0:
                            targetPosition = new Vector3(baseX, baseY, baseZ);
                            break;

                        // 2. 커피 카테고리 화면 (32번 마커) ➔ 화면 상단 탭으로 원 이동 (+Y)
                        case 32:
                            targetPosition = new Vector3(baseX, baseY + 0.189f, baseZ);
                            break;

                        // 3. 블렌디드 옵션 상세창 (420번 마커) ➔ 화면 우측 하단 장바구니 버튼 이동 (+X, -Y)
                        case 420:
                            targetPosition = new Vector3(baseX + 0.319f, baseY - 0.100f, baseZ);
                            break;

                        // 4. 최종 결제 방식 선택 화면 (768번 마커) ➔ 로그에 찍힌 물리 좌표 그대로 이동
                        case 768:
                            targetPosition = new Vector3(0.040f, -0.557f, 1.371f);
                            break;

                        default:
                            targetPosition = new Vector3(baseX, baseY, baseZ);
                            break;
                    }

                    if (fsm.target != null && fsm.target.world_size != null)
                    {
                        targetSize = new Vector2(fsm.target.world_size.w, fsm.target.world_size.h);
                    }
                    hasData = true;
                }
>>>>>>> Stashed changes
            }

            targetPosition = new Vector3(
                udpReceiver.latestState.fsm.target.world_position.x,
                -udpReceiver.latestState.fsm.target.world_position.y,
                udpReceiver.latestState.fsm.target.world_position.z
            );

            targetSize = new Vector2(
                udpReceiver.latestState.fsm.target.world_size.w,
                udpReceiver.latestState.fsm.target.world_size.h
            );

            recovery = udpReceiver.latestState.fsm.recovery;
        }
        else
        {
            if (
                runtimeStateReader == null ||
                runtimeStateReader.CurrentState == null ||
                !runtimeStateReader.HasTargetRect()
            )
            {
                return;
            }

            targetPosition = runtimeStateReader.GetTargetWorldPosition();
            targetSize = runtimeStateReader.GetTargetWorldSize();
            recovery = runtimeStateReader.IsRecoveryMode();
        }

<<<<<<< Updated upstream
        glowRing.position = Vector3.Lerp(
            glowRing.position,
            targetPosition,
            Time.deltaTime * moveSpeed
        );

        glowRing.localScale = new Vector3(
            targetSize.x * scaleFactor,
            targetSize.y * scaleFactor,
            1.0f
        );

        if (ringRenderer != null)
        {
            ringRenderer.material.color = recovery ? recoveryColor : normalColor;
=======
        // 2. 오브젝트 트랜스폼 연산 및 렌더링 스위칭
        if (glowRing != null)
        {
            if (hasData)
            {
                glowRing.gameObject.SetActive(true);
                
                // 보정된 타겟 좌표를 링에 대입
                glowRing.localPosition = targetPosition * positionScale;

                // 크기도 화면 스케일에 맞춰 부드럽게 매칭
                glowRing.localScale = new Vector3(
                    targetSize.x * scaleFactor,
                    targetSize.y * scaleFactor,
                    1.0f
                );
            }
            else
            {
                glowRing.gameObject.SetActive(false);
            }
>>>>>>> Stashed changes
        }
    }
}
