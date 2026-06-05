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
        try
        {
            udpClient = new UdpClient(port);
            receiveThread = new Thread(ReceiveLoop);
            receiveThread.IsBackground = true;
            receiveThread.Start();
            Debug.Log("[UDP] Receiver started on port " + port);
        }
        catch (Exception e)
        {
            Debug.LogError("[UDP] Start Error: " + e.Message);
        }
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
            try
            {
                latestState = JsonUtility.FromJson<RuntimeState>(json);
            }
            catch (Exception e)
            {
                Debug.LogError("[UDP] JSON Parsing Error: " + e.Message);
            }
        }
    }

    private void ReceiveLoop()
    {
        IPEndPoint remoteEndPoint = new IPEndPoint(IPAddress.Any, port);

        while (true)
        {
            try
            {
                byte[] receiveBytes = udpClient.Receive(ref remoteEndPoint);
                string json = Encoding.UTF8.GetString(receiveBytes);

                lock (lockObject)
                {
                    latestJson = json;
                }
            }
            catch (ThreadAbortException)
            {
                break;
            }
            catch (Exception e)
            {
                Debug.LogError("[UDP] Receive error: " + e.Message);
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

    // ====================================================================
    // [보안 락 우회 및 실시간 무선 연동 최적화 데이터 명세 구조 세팅]
    // 🚨 절대 주의: TargetData, WorldPosition 등은 중복 정의 에러(CS0101)를 
    // 방지하기 위해 RuntimeStateReader의 순정 구조를 다이렉트로 재활용합니다.
    // ====================================================================
    [System.Serializable]
    public class RuntimeState
    {
        public bool valid;
        public FSMData fsm; // 파이썬 json 키값 'fsm' 소문자 매핑용 고리
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
        public TargetData target; // RuntimeStateReader.cs에 있는 TargetData 클래스를 연동 사용
    }
}