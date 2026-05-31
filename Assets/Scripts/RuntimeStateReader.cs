using System;
using System.IO;
using UnityEngine;

public class RuntimeStateReader : MonoBehaviour
{
    [Header("Runtime JSON Settings")]
    [Tooltip("체크하면 Unity 프로젝트 루트 기준으로 vision/runtime_state.json을 읽습니다.")]
    public bool useProjectRelativePath = true;

    [Tooltip("useProjectRelativePath가 true일 때 사용할 상대 경로입니다.")]
    public string relativeJsonPath = "vision/runtime_state.json";

    [Tooltip("useProjectRelativePath가 false일 때 사용할 절대 경로입니다.")]
    public string absoluteJsonPath = "C:/Users/eorhk/OneDrive/문서/GitHub/mrkiosk/vision/runtime_state.json";

    [Header("Read Settings")]
    public float readInterval = 0.1f;

    public RuntimeStateData CurrentState { get; private set; }

    private float timer = 0f;
    private string resolvedJsonPath;

    private void Start()
    {
        resolvedJsonPath = ResolveJsonPath();
        Debug.Log("[RuntimeStateReader] JSON Path: " + resolvedJsonPath);
    }

    private void Update()
    {
        timer += Time.deltaTime;

        if (timer < readInterval)
        {
            return;
        }

        timer = 0f;
        ReadRuntimeState();
    }

    private string ResolveJsonPath()
    {
        if (!useProjectRelativePath)
        {
            return absoluteJsonPath;
        }

        // Application.dataPath = .../mrkiosk/Assets
        // 프로젝트 루트 = .../mrkiosk
        string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
        return Path.Combine(projectRoot, relativeJsonPath);
    }

    private void ReadRuntimeState()
    {
        if (!File.Exists(resolvedJsonPath))
        {
            Debug.LogWarning("[RuntimeStateReader] runtime_state.json not found: " + resolvedJsonPath);
            return;
        }

        try
        {
            string json = File.ReadAllText(resolvedJsonPath);

            if (string.IsNullOrWhiteSpace(json))
            {
                Debug.LogWarning("[RuntimeStateReader] JSON file is empty.");
                return;
            }

            CurrentState = JsonUtility.FromJson<RuntimeStateData>(json);

            if (CurrentState == null)
            {
                Debug.LogWarning("[RuntimeStateReader] Failed to parse JSON.");
                return;
            }
        }
        catch (Exception e)
        {
            Debug.LogWarning("[RuntimeStateReader] Failed to read JSON: " + e.Message);
        }
    }

    public bool HasValidState()
    {
        return CurrentState != null && CurrentState.valid;
    }

    public string GetFsmStateName()
    {
        if (CurrentState == null || CurrentState.fsm == null)
        {
            return "NO_DATA";
        }

        return CurrentState.fsm.state;
    }

    public int GetStateMarkerId()
    {
        if (CurrentState == null || CurrentState.state_marker == null)
        {
            return -1;
        }

        return CurrentState.state_marker.id;
    }

    public Vector3 GetTargetWorldPosition()
    {
        if (
            CurrentState == null ||
            CurrentState.fsm == null ||
            CurrentState.fsm.target == null ||
            CurrentState.fsm.target.world_position == null
        )
        {
            return Vector3.zero;
        }

        return new Vector3(
            CurrentState.fsm.target.world_position.x,
            -CurrentState.fsm.target.world_position.y,
            CurrentState.fsm.target.world_position.z
        );
    }

    public Vector3 GetReferenceTvec()
    {
        if (
            CurrentState == null ||
            CurrentState.reference == null ||
            CurrentState.reference.pose == null ||
            CurrentState.reference.pose.tvec == null ||
            CurrentState.reference.pose.tvec.Length < 3
        )
        {
            return Vector3.zero;
        }

        return new Vector3(
            CurrentState.reference.pose.tvec[0],
            CurrentState.reference.pose.tvec[1],
            CurrentState.reference.pose.tvec[2]
        );
    }

    public Vector3 GetReferenceRvec()
    {
        if (
            CurrentState == null ||
            CurrentState.reference == null ||
            CurrentState.reference.pose == null ||
            CurrentState.reference.pose.rvec == null ||
            CurrentState.reference.pose.rvec.Length < 3
        )
        {
            return Vector3.zero;
        }

        return new Vector3(
            CurrentState.reference.pose.rvec[0],
            CurrentState.reference.pose.rvec[1],
            CurrentState.reference.pose.rvec[2]
        );
    }

    public bool HasTargetRect()
    {
        if (
            CurrentState == null ||
            CurrentState.fsm == null ||
            CurrentState.fsm.target == null
        )
        {
            return false;
        }

        return CurrentState.fsm.target.world_size != null;
    }

    public Vector2 GetTargetWorldSize()
    {
        if (
            CurrentState == null ||
            CurrentState.fsm == null ||
            CurrentState.fsm.target == null ||
            CurrentState.fsm.target.world_size == null
        )
        {
            return Vector2.zero;
        }

        return new Vector2(
            CurrentState.fsm.target.world_size.w,
            CurrentState.fsm.target.world_size.h
        );
    }

    public bool IsRecoveryMode()
    {
        if (CurrentState == null || CurrentState.fsm == null)
        {
            return false;
        }

        return CurrentState.fsm.recovery;
    }
}

[Serializable]
public class RuntimeStateData
{
    public bool valid;
    public double timestamp;
    public TrackingData tracking;
    public ReferenceData reference;
    public StateMarkerData state_marker;
    public FsmData fsm;
}

[Serializable]
public class TrackingData
{
    public string reference_status;
    public string state_status;
    public int reference_missing_count;
    public int state_missing_count;
}

[Serializable]
public class ReferenceData
{
    public int id;
    public bool detected;
    public PoseData pose;
}

[Serializable]
public class PoseData
{
    public float[] rvec;
    public float[] tvec;
    public float[] marker_center;
    public float marker_area;
}

[Serializable]
public class StateMarkerData
{
    public bool detected;
    public int id;
}

[Serializable]
public class FsmData
{
    public string state;
    public string label;

    public int state_id;
    public int detected_state_id;

    public int expected_id;
    public int target_state_id;

    public bool recovery;

    public TargetData target;

    public RectPx rect_px;
}

[Serializable]
public class TargetData
{
    public string name;
    public string label;

    public RectPx rect_px;
    public WorldPosition world_position;
    public WorldSize world_size;
}

[Serializable]
public class WorldPosition
{
    public float x;
    public float y;
    public float z;
}

[Serializable]
public class WorldSize
{
    public float w;
    public float h;
}

[System.Serializable]
public class RectPx
{
    public float x;
    public float y;
    public float w;
    public float h;
}
