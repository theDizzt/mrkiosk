using UnityEngine;

public class GlowRingGuideController : MonoBehaviour
{
    [Header("Data Source Settings")]
    public bool useUdp = true;
    public UdpRuntimeStateReceiver udpReceiver;
    public RuntimeStateReader runtimeStateReader;

    [Header("Target Object")]
    public Transform glowRing;

    [Header("Movement")]
    public bool useLocalPosition = true;
    public float moveLerpSpeed = 8.0f;

    [Header("Adjustment Settings")]
    [Tooltip("파이썬 좌표계 보정 배율")]
    public Vector3 coordinateScale = Vector3.one;

    [Tooltip("파이썬 좌표계 보정 오프셋")]
    public Vector3 positionOffset = Vector3.zero;

    [Tooltip("링 크기 스케일 배율")]
    public float scaleFactor = 1.0f;

    [Header("Axis Mapping")]
    public bool invertY = true;

    private void Update()
    {
        if (glowRing == null)
        {
            return;
        }

        Vector3 targetPosition;
        Vector2 targetSize;
        bool hasData = TryGetTarget(out targetPosition, out targetSize);

        if (!hasData)
        {
            glowRing.gameObject.SetActive(false);
            return;
        }

        glowRing.gameObject.SetActive(true);

        Vector3 calibratedPosition = new Vector3(
            targetPosition.x * coordinateScale.x,
            targetPosition.y * coordinateScale.y,
            targetPosition.z * coordinateScale.z
        ) + positionOffset;

        if (useLocalPosition)
        {
            glowRing.localPosition = Vector3.Lerp(
                glowRing.localPosition,
                calibratedPosition,
                Time.deltaTime * moveLerpSpeed
            );
        }
        else
        {
            glowRing.position = Vector3.Lerp(
                glowRing.position,
                calibratedPosition,
                Time.deltaTime * moveLerpSpeed
            );
        }

        glowRing.localScale = new Vector3(
            targetSize.x * scaleFactor,
            targetSize.y * scaleFactor,
            1.0f
        );
    }

    private bool TryGetTarget(out Vector3 targetPosition, out Vector2 targetSize)
    {
        targetPosition = Vector3.zero;
        targetSize = Vector2.one;

        if (useUdp)
        {
            if (
                udpReceiver == null ||
                udpReceiver.latestState == null ||
                !udpReceiver.latestState.valid ||
                udpReceiver.latestState.fsm == null ||
                udpReceiver.latestState.fsm.target == null ||
                udpReceiver.latestState.fsm.target.world_position == null ||
                udpReceiver.latestState.fsm.target.world_size == null
            )
            {
                return false;
            }

            var pos = udpReceiver.latestState.fsm.target.world_position;
            var size = udpReceiver.latestState.fsm.target.world_size;

            targetPosition = new Vector3(
                pos.x,
                invertY ? -pos.y : pos.y,
                pos.z
            );

            targetSize = new Vector2(size.w, size.h);
            return true;
        }

        if (
            runtimeStateReader == null ||
            runtimeStateReader.CurrentState == null ||
            !runtimeStateReader.HasTargetRect()
        )
        {
            return false;
        }

        targetPosition = runtimeStateReader.GetTargetWorldPosition();
        targetSize = runtimeStateReader.GetTargetWorldSize();

        return true;
    }
}
