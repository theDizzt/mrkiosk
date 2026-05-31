using System;
using System.Collections;
using UnityEngine;

public class VRFormulaOperator : MonoBehaviour
{
    [Header("Operator HUD Elements")]
    // 인스펙터창에 확실하게 노출되도록 public으로 지정
    public GameObject targetIdTextObject;
    
    // 외부 패키지가 필요 없는 유니티 기본 TextMesh 시스템 사용
    private TextMesh targetIdTextMesh;

    [Header("Operator Menu Settings")]
    public int minTargetId = 0;
    public int maxTargetId = 29;

    public int ChosenTargetId { get; private set; } = 0;
    public bool IsSetupLocked { get; private set; } = false;

    void Start()
    {
        if (targetIdTextObject != null)
        {
            // 자식 오브젝트(NewText)에 붙은 기본 TextMesh 컴포넌트를 가져옵니다.
            targetIdTextMesh = targetIdTextObject.GetComponent<TextMesh>();
            targetIdTextObject.SetActive(true);
            UpdateHologramText();
        }
        else
        {
            Debug.LogWarning("[OPERATOR] targetIdTextObject 슬롯이 비어있습니다. NewText를 연결해 주세요.");
        }
    }

    void Update()
    {
        if (IsSetupLocked) return;

        // PC 테스트용 키보드 입력 가드 (이걸로 먼저 완벽하게 검증합니다)
        HandlePcDebugInput(); 
    }

    private void HandlePcDebugInput()
    {
        // 키보드 방향키 위(↑) 누르면 숫자 증가
        if (Input.GetKeyDown(KeyCode.UpArrow))
        {
            ChosenTargetId = Mathf.Min(ChosenTargetId + 1, maxTargetId);
            UpdateHologramText();
        }
        // 키보드 방향키 아래(↓) 누르면 숫자 감소
        else if (Input.GetKeyDown(KeyCode.DownArrow))
        {
            ChosenTargetId = Mathf.Max(ChosenTargetId - 1, minTargetId);
            UpdateHologramText();
        }
        
        // 키보드 엔터(Enter) 키를 누르면 최종 확정 및 소멸
        if (Input.GetKeyDown(KeyCode.Return))
        {
            LockAndDisableUI();
        }
    }

    private void LockAndDisableUI()
    {
        IsSetupLocked = true;
        if (targetIdTextObject != null)
        {
            targetIdTextObject.SetActive(false);
        }
        Debug.Log("[OPERATOR] 설정 확정 완료! Chosen ID: " + ChosenTargetId);
    }

    private void UpdateHologramText()
    {
        if (targetIdTextMesh != null)
        {
            targetIdTextMesh.text = "[Target ID: " + ChosenTargetId + "]";
        }
    }
}