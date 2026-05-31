using UnityEngine;

public class ButtonOutlineGuideController : MonoBehaviour
{
    [Header("Runtime State")]
    public RuntimeStateReader reader;

    [Header("Guide Root")]
    public GameObject guideRoot;

    [Header("Guide Bars")]
    public Transform topBar;
    public Transform bottomBar;
    public Transform leftBar;
    public Transform rightBar;

    [Header("Kiosk Screen Settings")]
    public float screenWidth = 1920f;
    public float screenHeight = 1080f;

    public float planeWidth = 1.0f;
    public float planeHeight = 0.5625f;

    [Header("Guide Visual Settings")]
    public float borderThickness = 0.015f;
    public float zOffset = 0.01f;
    public float padding = 0.02f;

    [Header("Runtime Conditions")]
    public bool requireValidReference = true;

    [Header("Forced Test Mode")]
    public bool useForcedTestTarget = false;
    public float testX = 1700f;
    public float testY = 930f;
    public float testWidth = 320f;
    public float testHeight = 110f;

    [Header("Debug")]
    public bool printDebugLog = true;

    private string lastState = "";
    private int lastStateId = -999;

    private void Start()
    {
        SetGuideVisible(false);
    }

    private void Update()
    {
        if (useForcedTestTarget)
        {
            UpdateGuideRect(testX, testY, testWidth, testHeight);
            SetGuideVisible(true);
            return;
        }

        if (reader == null || reader.CurrentState == null)
        {
            SetGuideVisible(false);
            return;
        }

        if (requireValidReference && !reader.CurrentState.valid)
        {
            SetGuideVisible(false);
            return;
        }

        if (!reader.HasTargetRect())
        {
            SetGuideVisible(false);
            return;
        }

        TargetData target = reader.CurrentState.fsm.target;

        UpdateGuideRect(
            target.x,
            target.y,
            target.width,
            target.height
        );

        SetGuideVisible(true);

        string state = reader.GetFsmStateName();
        int stateId = reader.GetStateMarkerId();

        if (printDebugLog && (state != lastState || stateId != lastStateId))
        {
            Debug.Log(
                "[ButtonOutlineGuide]\n" +
                "state: " + state + "\n" +
                "state id: " + stateId + "\n" +
                "target center: (" + target.x + ", " + target.y + ")\n" +
                "target size: (" + target.width + ", " + target.height + ")"
            );
        }

        lastState = state;
        lastStateId = stateId;
    }

    private void UpdateGuideRect(float x, float y, float width, float height)
    {
        float normalizedX = x / screenWidth;
        float normalizedY = y / screenHeight;

        float localX = (normalizedX - 0.5f) * planeWidth;
        float localY = (0.5f - normalizedY) * planeHeight;

        float rectWidth = (width / screenWidth) * planeWidth;
        float rectHeight = (height / screenHeight) * planeHeight;

        rectWidth += padding;
        rectHeight += padding;

        if (guideRoot != null)
        {
            guideRoot.transform.localPosition = new Vector3(localX, localY, zOffset);
            guideRoot.transform.localRotation = Quaternion.identity;
        }

        ApplyBarTransform(rectWidth, rectHeight);
    }

    private void ApplyBarTransform(float rectWidth, float rectHeight)
    {
        float halfWidth = rectWidth * 0.5f;
        float halfHeight = rectHeight * 0.5f;

        if (topBar != null)
        {
            topBar.localPosition = new Vector3(0f, halfHeight, 0f);
            topBar.localRotation = Quaternion.identity;
            topBar.localScale = new Vector3(rectWidth, borderThickness, borderThickness);
        }

        if (bottomBar != null)
        {
            bottomBar.localPosition = new Vector3(0f, -halfHeight, 0f);
            bottomBar.localRotation = Quaternion.identity;
            bottomBar.localScale = new Vector3(rectWidth, borderThickness, borderThickness);
        }

        if (leftBar != null)
        {
            leftBar.localPosition = new Vector3(-halfWidth, 0f, 0f);
            leftBar.localRotation = Quaternion.identity;
            leftBar.localScale = new Vector3(borderThickness, rectHeight, borderThickness);
        }

        if (rightBar != null)
        {
            rightBar.localPosition = new Vector3(halfWidth, 0f, 0f);
            rightBar.localRotation = Quaternion.identity;
            rightBar.localScale = new Vector3(borderThickness, rectHeight, borderThickness);
        }
    }

    private void SetGuideVisible(bool visible)
    {
        if (guideRoot != null && guideRoot.activeSelf != visible)
        {
            guideRoot.SetActive(visible);
        }
    }
}
