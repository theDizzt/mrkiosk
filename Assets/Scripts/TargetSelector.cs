using UnityEngine;
using UnityEngine.XR; // 메타 퀘스트 컨트롤러 직접 입력을 위한 네임스페이스
using System.Net;
using System.Net.Sockets;
using System.Text;

public class TargetSelector : MonoBehaviour
{
    [Header("UI Settings")]
    [Tooltip("Main Camera 자식으로 들어간 3D Text 오브젝트 자체")]
    public GameObject hologramTextObject;
    
    [Tooltip("기본 3D Text의 문자를 실시간으로 바꾸기 위한 컴포넌트")]
    public TextMesh targetTextMesh;

    [Header("Target ID Settings")]
    public int currentTargetId = 1;
    private const int MinId = 1;
    private const int MaxId = 30;

    [Header("UDP Network Settings (To Python)")]
    [Tooltip("파이썬 코드가 실행 중인 데스크톱 PC의 실제 IP 주소 (예: 192.168.0.X)")]
    public string pythonIpAddress = "127.0.0.1"; 
    [Tooltip("파이썬 측에서 지정한 입력 수신 포트 번호 (유니티 수신 포트인 5005와 구별)")]
    public int pythonPort = 5006; 

    private bool isLocked = false;
    private bool isStickReturned = true;
    private UdpClient udpClient;

    void Start()
    {
        isLocked = false;
        isStickReturned = true;
        
        // UDP 송신용 클라이언트 초기화
        udpClient = new UdpClient();

        if (hologramTextObject != null)
            hologramTextObject.SetActive(true);
            
        UpdateTextUI();
    }

    void Update()
    {
        if (isLocked) return; // 확정 후에는 조작 및 전송 잠금

        // 우측 컨트롤러 장치 입력 실시간 캡처
        var rightHandDevices = new System.Collections.Generic.List<InputDevice>();
        InputDevices.GetDevicesAtXRNode(XRNode.RightHand, rightHandDevices);

        if (rightHandDevices.Count > 0)
        {
            InputDevice rightHand = rightHandDevices[0];

            // 1. 우측 스틱 읽기 (상/하 튕기기)
            if (rightHand.TryGetFeatureValue(CommonUsages.primary2DAxis, out Vector2 stickValue))
            {
                HandleStickInput(stickValue);
            }

            // 2. 우측 A 버튼 읽기 (최종 확정)
            if (rightHand.TryGetFeatureValue(CommonUsages.primaryButton, out bool aButtonPressed))
            {
                if (aButtonPressed)
                {
                    ConfirmSelection();
                }
            }
        }
    }

    // 스틱을 위/아래로 튕길 때 숫자를 0~29 사이에서 1씩 증감시키는 로직
    private void HandleStickInput(Vector2 stickValue)
    {
        // 스틱이 중앙 부근으로 돌아오면 다시 튕길 수 있는 상태로 해제
        if (Mathf.Abs(stickValue.y) < 0.2f)
        {
            isStickReturned = true;
            return;
        }

        // 스틱을 계속 밀고 있어도 숫자가 마구 스크롤되지 않도록 가드
        if (!isStickReturned) return;

        if (stickValue.y > 0.5f) // 위로 튕김 ➔ 번호 증가
        {
            if (currentTargetId < MaxId)
            {
                currentTargetId++;
                UpdateTextUI();
                isStickReturned = false;
            }
        }
        else if (stickValue.y < -0.5f) // 아래로 튕김 ➔ 번호 감소
        {
            if (currentTargetId > MinId)
            {
                currentTargetId--;
                UpdateTextUI();
                isStickReturned = false;
            }
        }
    }

    // A 버튼을 눌렀을 때 실행되는 확정 및 전송 로직
    private void ConfirmSelection()
    {
        isLocked = true; // 1. 오퍼레이터 조작 즉시 잠금
        Handheld.Vibrate(); // 2. 성공 알림 진동(Haptic) 피드백

        // 3. [핵심] 결정된 Target ID 번호를 파이썬 비전 엔진으로 무선 전송
        SendTargetIdToPython(currentTargetId);

        // 4. 허공에 떠 있던 홀로그램 UI 삭제
        if (hologramTextObject != null)
        {
            hologramTextObject.SetActive(false);
        }

        Debug.Log($"[TargetSelector] 최종 확정 ID: {currentTargetId} ➔ 파이썬 전송 완료 및 UI 소멸");
    }

    // 파이썬이 파싱하기 편하게 JSON 포맷 파일 형태로 패킷을 날리는 함수
    private void SendTargetIdToPython(int id)
    {
        try
        {
            // 포맷 형식: {"selected_target_id": 3}
            string jsonMessage = $"{{\"selected_target_id\": {id}}}";
            byte[] data = Encoding.UTF8.GetBytes(jsonMessage);

            udpClient.Send(data, data.Length, pythonIpAddress, pythonPort);
            Debug.Log($"[UDP Send] 성공 ➔ PC({pythonIpAddress}:{pythonPort}): {jsonMessage}");
        }
        catch (System.Exception e)
        {
            Debug.LogError("[UDP Send Error] 파이썬으로 번호 전송 실패: " + e.Message);
        }
    }

    // 화면의 글자를 실시간 변경해주는 함수
    private void UpdateTextUI()
    {
        if (targetTextMesh != null)
        {
            targetTextMesh.text = $"[Target ID: {currentTargetId}]";
        }
    }

    void OnDestroy()
    {
        if (udpClient != null)
        {
            udpClient.Close();
        }
    }
}