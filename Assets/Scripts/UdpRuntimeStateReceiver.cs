using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;

public class UdpRuntimeStateReceiver : MonoBehaviour
{
    [Header("UDP Receive Settings")]
    public int listenPort = 5005;

    [Header("Target Selector")]
    public TargetSelector targetSelector;

    [Header("Runtime Debug")]
    public bool logReceivedMessage = false;

    private UdpClient udpClient;
    private Thread receiveThread;
    private bool isRunning = false;

    private readonly ConcurrentQueue<string> messageQueue = new ConcurrentQueue<string>();

    private bool hasHandledPaymentReset = false;

    public RuntimeState latestState;
    public bool hasLatestState = false;

    public Vector3 latestTargetWorldPosition;
    public Vector2 latestTargetWorldSize;
    public bool hasTarget = false;

    public string latestTargetName;
    public string latestTargetLabel;
    public int latestStateId;
    public int latestDetectedStateId;
    public int latestTargetStateId;
    public string latestFsmMessage;

    private void Start()
    {
        StartReceiver();

        if (targetSelector == null)
        {
            targetSelector = FindObjectOfType<TargetSelector>();
        }
    }

    private void Update()
    {
        while (messageQueue.TryDequeue(out string json))
        {
            ProcessRuntimeJson(json);
        }
    }

    private void StartReceiver()
    {
        try
        {
            udpClient = new UdpClient(listenPort);
            isRunning = true;

            receiveThread = new Thread(ReceiveLoop);
            receiveThread.IsBackground = true;
            receiveThread.Start();

            Debug.Log($"[UdpRuntimeStateReceiver] UDP 수신 시작: Port {listenPort}");
        }
        catch (Exception e)
        {
            Debug.LogError("[UdpRuntimeStateReceiver] UDP 수신 시작 실패: " + e.Message);
        }
    }

    private void ReceiveLoop()
    {
        IPEndPoint remoteEndPoint = new IPEndPoint(IPAddress.Any, listenPort);

        while (isRunning)
        {
            try
            {
                byte[] data = udpClient.Receive(ref remoteEndPoint);
                string message = Encoding.UTF8.GetString(data);

                messageQueue.Enqueue(message);
            }
            catch (SocketException)
            {
                // 종료 시 발생 가능
            }
            catch (Exception e)
            {
                Debug.LogError("[UdpRuntimeStateReceiver] 수신 오류: " + e.Message);
            }
        }
    }

    private void ProcessRuntimeJson(string json)
    {
        if (string.IsNullOrWhiteSpace(json))
        {
            return;
        }

        if (logReceivedMessage)
        {
            Debug.Log("[UdpRuntimeStateReceiver] JSON: " + json);
        }

        try
        {
            RuntimeState state = JsonUtility.FromJson<RuntimeState>(json);

            if (state == null)
            {
                return;
            }

            latestState = state;
            hasLatestState = true;

            UpdateCachedFields(state);
            HandlePaymentCompleteReset(state);
        }
        catch (Exception e)
        {
            Debug.LogError("[UdpRuntimeStateReceiver] JSON 파싱 실패: " + e.Message);
        }
    }

    private void UpdateCachedFields(RuntimeState state)
    {
        hasTarget = false;

        if (state.fsm != null)
        {
            latestStateId = state.fsm.state_id;
            latestDetectedStateId = state.fsm.detected_state_id;
            latestTargetStateId = state.fsm.target_state_id;
            latestTargetName = state.fsm.target_name;
            latestTargetLabel = state.fsm.target_label;
            latestFsmMessage = state.fsm.message;

            if (state.fsm.target != null && state.fsm.target.world_position != null)
            {
                RuntimeVector3 pos = state.fsm.target.world_position;

                latestTargetWorldPosition = new Vector3(
                    pos.x,
                    pos.y,
                    pos.z
                );

                if (state.fsm.target.world_size != null)
                {
                    RuntimeSize size = state.fsm.target.world_size;

                    latestTargetWorldSize = new Vector2(
                        size.w,
                        size.h
                    );
                }

                hasTarget = true;
            }
        }
    }

    private void HandlePaymentCompleteReset(RuntimeState state)
    {
        if (state.fsm == null)
        {
            return;
        }

        bool isPaymentCompleteReset = state.fsm.message == "payment_complete_reset";

        if (isPaymentCompleteReset)
        {
            if (!hasHandledPaymentReset)
            {
                if (targetSelector == null)
                {
                    targetSelector = FindObjectOfType<TargetSelector>();
                }

                if (targetSelector != null)
                {
                    targetSelector.ResetSelectorForNextOrder();
                    Debug.Log("[UdpRuntimeStateReceiver] payment_complete_reset 감지 -> TargetSelector 재활성화");
                }
                else
                {
                    Debug.LogWarning("[UdpRuntimeStateReceiver] TargetSelector를 찾지 못했습니다.");
                }

                hasHandledPaymentReset = true;
            }
        }
        else
        {
            hasHandledPaymentReset = false;
        }
    }

    public bool TryGetTarget(out Vector3 position, out Vector2 size)
    {
        position = latestTargetWorldPosition;
        size = latestTargetWorldSize;

        return hasTarget;
    }

    private void OnDestroy()
    {
        StopReceiver();
    }

    private void OnApplicationQuit()
    {
        StopReceiver();
    }

    private void StopReceiver()
    {
        isRunning = false;

        if (udpClient != null)
        {
            udpClient.Close();
            udpClient = null;
        }

        if (receiveThread != null)
        {
            receiveThread.Abort();
            receiveThread = null;
        }

        Debug.Log("[UdpRuntimeStateReceiver] UDP 수신 종료");
    }
}

[Serializable]
public class RuntimeState
{
    public bool valid;
    public double timestamp;
    public RuntimeTracking tracking;
    public RuntimeReference reference;
    public RuntimeStateMarker state_marker;
    public RuntimeFsm fsm;
}

[Serializable]
public class RuntimeTracking
{
    public string reference_status;
    public string state_status;
    public int reference_missing_count;
    public int state_missing_count;
}

[Serializable]
public class RuntimeReference
{
    public int id;
    public bool detected;
    public RuntimePose pose;
}

[Serializable]
public class RuntimePose
{
    public float[] rvec;
    public float[] tvec;
    public float[] marker_center;
    public float marker_area;
}

[Serializable]
public class RuntimeStateMarker
{
    public bool detected;
    public int id;
}

[Serializable]
public class RuntimeFsm
{
    public string state;
    public string label;

    public int state_id;
    public int detected_state_id;
    public int target_state_id;
    public int expected_id;

    public bool recovery;
    public string message;

    public string target_name;
    public string target_label;

    public RuntimeRect target_rect;
    public RuntimeTarget target;
}

[Serializable]
public class RuntimeRect
{
    public float x;
    public float y;
    public float w;
    public float h;
}

[Serializable]
public class RuntimeTarget
{
    public RuntimeVector3 world_position;
    public RuntimeSize world_size;
    public string label;
}

[Serializable]
public class RuntimeVector3
{
    public float x;
    public float y;
    public float z;
}

[Serializable]
public class RuntimeSize
{
    public float w;
    public float h;
}