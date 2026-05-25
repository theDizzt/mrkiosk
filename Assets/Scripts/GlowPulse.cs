using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GlowPulse : MonoBehaviour
{
    private Vector3 baseScale;

    [Header("Pulse Settings")]
    public float pulseSpeed = 3.0f;
    public float pulseAmount = 0.08f;

    void Start()
    {
        baseScale = transform.localScale;
    }

    void Update()
    {
        float scale = 1.0f + Mathf.Sin(Time.time * pulseSpeed) * pulseAmount;
        transform.localScale = baseScale * scale;
    }
}
