using System;
using System.IO;
using UnityEngine;

public class RuntimeStateReader : MonoBehaviour
{
    // 읽는 속도 향상을 위해 임시로 절대 경로로 지정
    [Header("JSON file path")]
    public string jsonFilePath = "C:/Users/eorhk/OneDrive/문서/GitHub/mrkiosk/vision/runtime_state.json";

    [Header("Object to move")]
    public Transform guideObject;

    [Header("Scale for converting Python meters to Unity world")]
    public float positionScale = 1.0f;

    [Header("Polling interval (seconds)")]
    public float updateInterval = 0.1f;

    [Header("Smooth movement")]
    public float moveLerpSpeed = 0.4f;

    private float timer = 0f;
    private string lastTimestamp = "";

    // 색상 변경용 Renderer 참조
    private Renderer guideRenderer;

    // 목표 위치를 저장해서 Lerp 이동에 사용
    private Vector3 targetPosition;

    [Serializable]
    public class RuntimeState
    {
        public string timestamp;
        public string state;
        public int marker_id;
        public float[] rvec;
        public float[] tvec;
        public Payload payload;
    }

    [Serializable]
    public class Payload
    {
        public string screen;
        public string target_button;
        public Position position;
        public Offset offset_from_marker;
        public string message;
    }

    [Serializable]
    public class Position
    {
        public float x;
        public float y;
    }

    [Serializable]
    public class Offset
    {
        public float x;
        public float y;
        public float z;
    }

    void Start()
    {
        if (guideObject != null)
        {
            guideRenderer = guideObject.GetComponent<Renderer>();
            targetPosition = guideObject.position;
        }
    }

    void Update()
    {
        // guideObject가 있으면 매 프레임 부드럽게 목표 위치로 이동
        if (guideObject != null)
        {
            guideObject.position = Vector3.Lerp(
                guideObject.position,
                targetPosition,
                moveLerpSpeed
            );

            // 평면 가이드처럼 보이도록 회전 고정
            guideObject.rotation = Quaternion.Euler(90f, 0f, 0f);
        }

        timer += Time.deltaTime;

        if (timer < updateInterval)
            return;

        timer = 0f;
        ReadAndApplyRuntimeState();
    }

    void ReadAndApplyRuntimeState()
    {
        if (guideObject == null)
        {
            Debug.LogWarning("Guide Object is not assigned.");
            return;
        }

        if (!File.Exists(jsonFilePath))
        {
            Debug.LogWarning("runtime_state.json not found: " + jsonFilePath);
            return;
        }

        try
        {
            string json = File.ReadAllText(jsonFilePath);
            RuntimeState data = JsonUtility.FromJson<RuntimeState>(json);

            if (data == null)
            {
                Debug.LogWarning("Failed to parse runtime_state.json");
                return;
            }

            if (string.IsNullOrEmpty(data.timestamp))
            {
                Debug.LogWarning("timestamp is empty in runtime_state.json");
                return;
            }

            if (data.timestamp == lastTimestamp)
            {
                return;
            }

            lastTimestamp = data.timestamp;

            Vector3 newPosition = ConvertPythonPoseToUnity(data);
            
            // 즉시 이동 대신 목표 위치만 갱신
            targetPosition = newPosition;

            // 상태별 색 반영
            ApplyStateColor(data.state);

            Debug.Log($"[RuntimeState] state={data.state}, marker_id={data.marker_id}, pos={newPosition}");
        }
        catch (Exception e)
        {
            Debug.LogError("Error reading runtime_state.json: " + e.Message);
        }
    }

    Vector3 ConvertPythonPoseToUnity(RuntimeState data)
    {
        float x = 0f;
        float y = 0f;
        float z = 0f;

        // Python의 tvec를 기본 위치로 사용
        if (data.tvec != null && data.tvec.Length >= 3)
        {
            x = data.tvec[0];
            y = data.tvec[1];
            z = data.tvec[2];
        }

        // payload의 offset_from_marker가 있으면 추가 반영
        if (data.payload != null && data.payload.offset_from_marker != null)
        {
            x += data.payload.offset_from_marker.x;
            y += data.payload.offset_from_marker.y;
            z += data.payload.offset_from_marker.z;
        }

        // OpenCV 카메라 좌표계를 Unity 좌표계로 단순 변환
        // 필요하면 나중에 축 방향 맞춰서 수정
        return new Vector3(
            x * positionScale,
            -y * positionScale,
            z * positionScale
        );
    }

    // 상태별 색상 변경 함수
    void ApplyStateColor(string state)
    {
        if (guideRenderer == null)
            return;

        Color targetColor = Color.white;

        switch (state)
        {
            case "IDLE":
                targetColor = Color.gray;
                break;
            case "LISTENING":
                targetColor = Color.blue;
                break;
            case "MENU_GUIDE":
                targetColor = Color.green;
                break;
            case "OPTION_GUIDE":
                targetColor = Color.yellow;
                break;
            case "PAYMENT_GUIDE":
                targetColor = Color.red;
                break;
            case "CONFIRM":
                targetColor = Color.cyan;
                break;
            case "ERROR_RECOVERY":
                targetColor = new Color(1f, 0.5f, 0f);
                break;
            case "FAIL_SAFE":
                targetColor = new Color(0.6f, 0.2f, 1f);
                break;
        }

        guideRenderer.material.color = targetColor;
    }
}
