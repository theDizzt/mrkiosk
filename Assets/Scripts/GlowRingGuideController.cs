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

        if (useUdp)
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
                return;
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
        }
    }
}
