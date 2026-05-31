using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class UdpRuntimeStateReceiver : MonoBehaviour
{
    [Header("UDP Settings")]
    public int port = 5005;

    [Header("Latest State")]
    public RuntimeState latestState;

    private UdpClient udpClient;
    private Thread receiveThread;
    private string latestJson;
    private readonly object lockObject = new object();

    void Start()
    {
        udpClient = new UdpClient(port);
        receiveThread = new Thread(ReceiveLoop);
        receiveThread.IsBackground = true;
        receiveThread.Start();

        Debug.Log("[UDP] Receiver started on port " + port);
    }

    void Update()
    {
        string json = null;

        lock (lockObject)
        {
            if (!string.IsNullOrEmpty(latestJson))
            {
                json = latestJson;
                latestJson = null;
            }
        }

        if (!string.IsNullOrEmpty(json))
        {
            latestState = JsonUtility.FromJson<RuntimeState>(json);
        }
    }

    private void ReceiveLoop()
    {
        IPEndPoint remoteEndPoint = new IPEndPoint(IPAddress.Any, port);

        while (true)
        {
            try
            {
                byte[] data = udpClient.Receive(ref remoteEndPoint);
                string json = Encoding.UTF8.GetString(data);

                lock (lockObject)
                {
                    latestJson = json;
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning("[UDP] Receive error: " + e.Message);
            }
        }
    }

    void OnDestroy()
    {
        if (receiveThread != null)
        {
            receiveThread.Abort();
            receiveThread = null;
        }

        if (udpClient != null)
        {
            udpClient.Close();
            udpClient = null;
        }
    }

    [System.Serializable]
    public class RuntimeState
    {
        public bool valid;
        public FSMData fsm;
    }

    [System.Serializable]
    public class FSMData
    {
        public string state;
        public string label;
        public int state_id;
        public int detected_state_id;
        public int target_state_id;
        public int expected_id;
        public bool recovery;
        public TargetData target;
    }

    [System.Serializable]
    public class TargetData
    {
        public string name;
        public string label;
        public RectPx rect_px;
        public WorldPosition world_position;
        public WorldSize world_size;
    }

    [System.Serializable]
    public class RectPx
    {
        public float x;
        public float y;
        public float w;
        public float h;
    }

    [System.Serializable]
    public class WorldPosition
    {
        public float x;
        public float y;
        public float z;
    }

    [System.Serializable]
    public class WorldSize
    {
        public float w;
        public float h;
    }

}
