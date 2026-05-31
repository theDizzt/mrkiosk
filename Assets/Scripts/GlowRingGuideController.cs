using UnityEngine;

public class GlowRingGuideController : MonoBehaviour
{
    [Header("References")]
    public RuntimeStateReader runtimeStateReader;
    public Transform glowRing;

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
        if (runtimeStateReader == null || glowRing == null)
        {
            return;
        }

        if (!runtimeStateReader.HasTargetRect())
        {
            return;
        }

        Vector3 targetPosition = runtimeStateReader.GetTargetWorldPosition();

        glowRing.position = Vector3.Lerp(
            glowRing.position,
            targetPosition,
            Time.deltaTime * moveSpeed
        );

        Vector2 targetSize = runtimeStateReader.GetTargetWorldSize();

        glowRing.localScale = new Vector3(
            targetSize.x * scaleFactor,
            targetSize.y * scaleFactor,
            1.0f
        );

        if (ringRenderer != null)
        {
            ringRenderer.material.color =
                runtimeStateReader.IsRecoveryMode()
                    ? recoveryColor
                    : normalColor;
        }
    }
}
