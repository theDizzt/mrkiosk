using UnityEngine;
using UnityEngine.XR;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Text;

public class TargetSelector : MonoBehaviour
{
    [Header("UI Settings")]
    public GameObject hologramTextObject;
    public TextMesh targetTextMesh;

    [Header("Target ID Settings")]
    public int currentTargetId = 1;
    public int minTargetId = 1;
    public int maxTargetId = 30;

    [Header("UDP Network Settings To Python")]
    [Tooltip("Python이 실행 중인 PC의 Wi-Fi IPv4 주소")]
    public string pythonIpAddress = "192.168.0.23";

    [Tooltip("Python app_aruco_dual.py가 수신하는 포트")]
    public int pythonPort = 5006;

    [Header("Selector State")]
    [SerializeField] private bool isLocked = false;

    private bool isStickReturned = true;
    private bool wasAButtonPressed = false;
    private UdpClient udpClient;

    private void Start()
    {
        udpClient = new UdpClient();

        isLocked = false;
        isStickReturned = true;
        wasAButtonPressed = false;

        if (hologramTextObject != null)
        {
            hologramTextObject.SetActive(true);
        }

        UpdateTextUI();

        Debug.Log(
            $"[TargetSelector START] Python IP={pythonIpAddress}, " +
            $"Port={pythonPort}, Current Menu ID={currentTargetId}"
        );
    }

    private void Update()
    {
        if (isLocked)
        {
            return;
        }

        List<InputDevice> rightHandDevices = new List<InputDevice>();
        InputDevices.GetDevicesAtXRNode(XRNode.RightHand, rightHandDevices);

        if (rightHandDevices.Count == 0)
        {
            return;
        }

        InputDevice rightHand = rightHandDevices[0];

        if (rightHand.TryGetFeatureValue(CommonUsages.primary2DAxis, out Vector2 stickValue))
        {
            HandleStickInput(stickValue);
        }

        if (rightHand.TryGetFeatureValue(CommonUsages.primaryButton, out bool aButtonPressed))
        {
            if (aButtonPressed && !wasAButtonPressed)
            {
                ConfirmSelection();
            }

            wasAButtonPressed = aButtonPressed;
        }
    }

    private void HandleStickInput(Vector2 stickValue)
    {
        if (Mathf.Abs(stickValue.y) < 0.2f)
        {
            isStickReturned = true;
            return;
        }

        if (!isStickReturned)
        {
            return;
        }

        if (stickValue.y > 0.5f)
        {
            if (currentTargetId < maxTargetId)
            {
                currentTargetId++;
                UpdateTextUI();
                isStickReturned = false;

                Debug.Log($"[TargetSelector] Menu ID 증가: {currentTargetId}");
            }
        }
        else if (stickValue.y < -0.5f)
        {
            if (currentTargetId > minTargetId)
            {
                currentTargetId--;
                UpdateTextUI();
                isStickReturned = false;

                Debug.Log($"[TargetSelector] Menu ID 감소: {currentTargetId}");
            }
        }
    }

    private void ConfirmSelection()
    {
        isLocked = true;

        Handheld.Vibrate();

        SendTargetIdToPython(currentTargetId);

        if (hologramTextObject != null)
        {
            hologramTextObject.SetActive(false);
        }

        Debug.Log($"[TargetSelector] 최종 확정 ID: {currentTargetId} 전송, 메뉴 선택 UI 숨김");
    }

    private void SendTargetIdToPython(int id)
    {
        try
        {
            string jsonMessage = $"{{\"selected_target_id\": {id}}}";
            byte[] data = Encoding.UTF8.GetBytes(jsonMessage);

            udpClient.Send(data, data.Length, pythonIpAddress, pythonPort);

            Debug.Log($"[UDP Send] 성공 -> {pythonIpAddress}:{pythonPort} <= {jsonMessage}");
        }
        catch (System.Exception e)
        {
            Debug.LogError("[UDP Send Error] Python으로 번호 전송 실패: " + e.Message);
        }
    }

    private void UpdateTextUI()
    {
        if (targetTextMesh != null)
        {
            targetTextMesh.text = $"[Menu ID: {currentTargetId}]";
        }
    }

    public void ResetSelectorForNextOrder()
    {
        isLocked = false;
        wasAButtonPressed = false;
        isStickReturned = true;

        if (hologramTextObject != null)
        {
            hologramTextObject.SetActive(true);
        }

        UpdateTextUI();

        Debug.Log("[TargetSelector] 주문 완료 감지: 다음 메뉴 선택 UI 다시 활성화");
    }

    private void OnDestroy()
    {
        if (udpClient != null)
        {
            udpClient.Close();
            udpClient = null;
        }
    }
}