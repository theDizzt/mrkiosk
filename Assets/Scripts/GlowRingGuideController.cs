// Assets/Scripts/GlowRingGuideController.cs
using UnityEngine;

public class GlowRingGuideController : MonoBehaviour
{
    [Header("Data Source Settings")]
    public bool useUdp = true;
    public UdpRuntimeStateReceiver udpReceiver;
    public RuntimeStateReader runtimeStateReader;

    [Header("Target Object")]
    [Tooltip("실제로 움직일 글로우 링 오브젝트")]
    public Transform glowRing;

    [Tooltip("키오스크 화면 기준 부모 오브젝트. 보통 KioskScreen 또는 KioskAnchor")]
    public Transform kioskScreenRoot;

    [Header("Kiosk Screen Pixel Settings")]
    public float screenWidth = 1024f;
    public float screenHeight = 720f;

    [Header("Unity Plane Size")]
    public float planeWidth = 1.0f;
    public float planeHeight = 0.703125f; // 720 / 1024

    [Header("Guide Visual Settings")]
    public float zOffset = 0.01f;
    public float moveSpeed = 6.0f;
    public float scaleFactor = 1.2f;

    [Header("Colors")]
    public Color normalColor = new Color(1.0f, 0.373f, 0.082f); // #FF5F15
    public Color recoveryColor = Color.red;

    [Header("Debug")]
    public bool printDebugLog = true;

    private Renderer ringRenderer;
    private string lastTargetName = "";

    private void Start()
    {
        if (glowRing == null)
        {
            Debug.LogWarning("[GlowRingGuide] glowRing is not assigned.");
            return;
        }

        ringRenderer = glowRing.GetComponent<Renderer>();

        if (kioskScreenRoot != null)
        {
            glowRing.SetParent(kioskScreenRoot, false);
        }

        glowRing.localRotation = Quaternion.identity;
        glowRing.gameObject.SetActive(false);
    }

    private void Update()
    {
        if (glowRing == null)
        {
            return;
        }

        float x;
        float y;
        float w;
        float h;
        bool recovery;
        string targetName;

        bool hasTarget = TryGetTargetRect(
            out x,
            out y,
            out w,
            out h,
            out recovery,
            out targetName
        );

        if (!hasTarget)
        {
            glowRing.gameObject.SetActive(false);
            return;
        }

        glowRing.gameObject.SetActive(true);

        Vector3 targetLocalPosition = RectPxToLocalPosition(x, y, w, h);
        Vector3 targetLocalScale = RectPxToLocalScale(w, h);

        glowRing.localPosition = Vector3.Lerp(
            glowRing.localPosition,
            targetLocalPosition,
            Time.deltaTime * moveSpeed
        );

        glowRing.localScale = Vector3.Lerp(
            glowRing.localScale,
            targetLocalScale,
            Time.deltaTime * moveSpeed
        );

        glowRing.localRotation = Quaternion.identity;

        if (ringRenderer != null)
        {
            ringRenderer.material.color = recovery ? recoveryColor : normalColor;
        }

        if (printDebugLog && targetName != lastTargetName)
        {
            Debug.Log(
                "[GlowRingGuide]\n" +
                "target: " + targetName + "\n" +
                "rect_px: (" + x + ", " + y + ", " + w + ", " + h + ")\n" +
                "localPosition: " + targetLocalPosition + "\n" +
                "localScale: " + targetLocalScale
            );

            lastTargetName = targetName;
        }
    }

    private bool TryGetTargetRect(
        out float x,
        out float y,
        out float w,
        out float h,
        out bool recovery,
        out string targetName
    )
    {
        x = 0f;
        y = 0f;
        w = 0f;
        h = 0f;
        recovery = false;
        targetName = "NO_TARGET";

        if (useUdp)
        {
            if (
                udpReceiver == null ||
                udpReceiver.latestState == null ||
                !udpReceiver.latestState.valid ||
                udpReceiver.latestState.fsm == null ||
                udpReceiver.latestState.fsm.target == null ||
                udpReceiver.latestState.fsm.target.rect_px == null
            )
            {
                return false;
            }

            var target = udpReceiver.latestState.fsm.target;
            var rect = target.rect_px;

            x = rect.x;
            y = rect.y;
            w = rect.w;
            h = rect.h;
            recovery = udpReceiver.latestState.fsm.recovery;
            targetName = target.name;

            return true;
        }

        if (
            runtimeStateReader == null ||
            runtimeStateReader.CurrentState == null ||
            !runtimeStateReader.CurrentState.valid ||
            runtimeStateReader.CurrentState.fsm == null ||
            runtimeStateReader.CurrentState.fsm.target == null ||
            runtimeStateReader.CurrentState.fsm.target.rect_px == null
        )
        {
            return false;
        }

        TargetData jsonTarget = runtimeStateReader.CurrentState.fsm.target;
        RectPx jsonRect = jsonTarget.rect_px;

        x = jsonRect.x;
        y = jsonRect.y;
        w = jsonRect.w;
        h = jsonRect.h;
        recovery = runtimeStateReader.IsRecoveryMode();
        targetName = jsonTarget.name;

        return true;
    }

    private Vector3 RectPxToLocalPosition(float x, float y, float width, float height)
    {
        float centerX = x + width * 0.5f;
        float centerY = y + height * 0.5f;

        float normalizedX = centerX / screenWidth;
        float normalizedY = centerY / screenHeight;

        float localX = (normalizedX - 0.5f) * planeWidth;
        float localY = (0.5f - normalizedY) * planeHeight;

        return new Vector3(localX, localY, zOffset);
    }

    private Vector3 RectPxToLocalScale(float width, float height)
    {
        float localWidth = (width / screenWidth) * planeWidth;
        float localHeight = (height / screenHeight) * planeHeight;

        return new Vector3(
            localWidth * scaleFactor,
            localHeight * scaleFactor,
            1.0f
        );
    }
}
