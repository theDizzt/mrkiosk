using UnityEngine;

/// <summary>
/// [Track B] 10-bit 마커 기반 Reactive FSM 통합 제어 메인 엔진
/// 설계 목적: 텍스트프리(Text-Free) 구현 및 시니어 인지부하 최소화를 위한 중앙 제어 플러그인
/// </summary>
public class FSMMetaPathEngine : MonoBehaviour
{
    [Header("[1] Target Configuration (단일 입력 제어점)")]
    [Tooltip("사용자가 모바일 앱이나 가상 패널을 통해 최초 선택한 목표 메뉴 번호 (0 ~ 29)")]
    [Range(0, 29)]
    [SerializeField] private int targetCartItemID = 14; 

    [Header("[2] Output Modules (출력부 조립 인터페이스)")]
    public ARGuidanceManager arManager;
    public TTSManager ttsManager;

    private int targetCategory;      
    private int targetMenuHash;      
    
    // 상태 추적 변수
    private int previousPhase = -1;
    private int previousStateCode = -1; 

    public int TargetCartItemID
    {
        get => targetCartItemID;
        set => SetupMetaPath(value);
    }

    private void Awake()
    {
        SetupMetaPath(targetCartItemID);
    }

    public void SetupMetaPath(int menuID)
    {
        targetCartItemID = Mathf.Clamp(menuID, 0, 29);
        targetCategory = targetCartItemID / 6;  
        targetMenuHash = targetCartItemID % 6;  
        
        // 재진입 시 FSM 내부 상태 완벽 초기화
        previousPhase = -1;
        previousStateCode = -1;
        
        Debug.Log($"[FSM Core] 메타 경로 바인딩 완료 -> MenuID: {targetCartItemID} | Category: {targetCategory} | Hash: {targetMenuHash}");
    }

    public void ProcessStateCode(int stateCode)
    {
        if (stateCode < 0 || stateCode > 1023) return; 

        // 상태 변화가 없을 경우 하위 로직(Dispatch) 실행 차단 (Edge Triggering)
        if (stateCode == previousStateCode) return;

        int phase = (stateCode >> 8) & 0x03;
        int entity = stateCode & 0xFF;

        // [Loop Reset] 
        if (previousPhase == 0b11 && phase == 0b00 && entity == 0)
        {
            HandleOrderCompleted();
            previousPhase = phase;
            previousStateCode = stateCode;
            return; 
        }

        switch (phase)
        {
            case 0b00: RoutePhase00_Menu(entity); break;      // Phase 00
            case 0b01: RoutePhase01_Option(entity); break;    // Phase 01
            case 0b10: RoutePhase10_Cart(entity); break;      // Phase 10
            case 0b11: RoutePhase11_Payment(entity); break;   // Phase 11
        }

        previousPhase = phase;
        previousStateCode = stateCode; // 현재 상태 캐싱
    }

    private void RoutePhase00_Menu(int entity)
    {
        if (entity == 0)
        {
            DispatchGuidance("ORDER_TYPE_BUTTON", "매장에서 식사하실 건가요? 포장 주문 하실 건가요?");
            return;
        }

        int currentCategory = (entity >> 5) & 0x07;

        // 유효 범위(0~4)를 벗어난 노이즈 데이터 필터링
        if (currentCategory > 4) return;

        if (currentCategory != targetCategory)
        {
            DispatchGuidance($"CATEGORY_TAB_{targetCategory}", "화면 위쪽의 메뉴 탭을 눌러주세요.", isException: true);
        }
        else
        {
            DispatchGuidance($"MENU_GRID_{targetMenuHash}", "원하시는 메뉴를 선택해주세요.");
        }
    }

    private void RoutePhase01_Option(int entity)
    {
        int menuTracker = (entity >> 5) & 0x07;     
        int temperature = (entity >> 3) & 0x03;     
        int isSugarSelected = (entity >> 2) & 0x01; 
        int isIceSelected = (entity >> 1) & 0x01;   

        // 2비트 한계치(0x03) 및 유효 범위(0~5)를 벗어난 노이즈 데이터 필터링
        if (temperature == 0x03 || menuTracker > 5) return;

        if (menuTracker != targetMenuHash)
        {
            DispatchGuidance("CANCEL_BUTTON", "메뉴를 잘못 선택하셨습니다. 취소 버튼을 눌러주세요.", isException: true);
            return;
        }

        if (temperature == 0x00)
        {
            DispatchGuidance("TEMPERATURE_AREA", "온도를 선택해주세요. 왼쪽은 시원한 음료, 오른쪽은 뜨거운 음료입니다.");
        }
        else if (isSugarSelected == 0)
        {
            DispatchGuidance("SUGAR_AREA", "당도를 선택해주세요. 왼쪽부터 덜 달게, 보통, 달게입니다.");
        }
        else 
        {
            if (temperature == 0x02 || isIceSelected == 1)
            {
                DispatchGuidance("INSERT_CART_BUTTON", "버튼을 눌러 장바구니에 담아주세요.");
            }
            else
            {
                DispatchGuidance("ICE_AREA", "얼음량을 선택해주세요. 왼쪽부터 적게, 보통, 많이입니다.");
            }
        }
    }

    private void RoutePhase10_Cart(int entity)
    {
        // Note: 하위 2비트(entity & 0x03)는 현재 장바구니 수량(Quantity) 확장을 위한 예약 공간으로 비워둠 (CS0219 방지)
        int cartItemID = (entity >> 2) & 0x3F; 

        // 원시 ID 유효 범위 검증 (0~29)
        if (cartItemID > 29) return;

        if (cartItemID != targetCartItemID)
        {
            DispatchGuidance("REMOVE_CART_BUTTON", "잘못된 메뉴를 담았습니다. 버튼을 눌러 장바구니에서 빼주세요.", isException: true);
        }
        else
        {
            DispatchGuidance("GO_PAYMENT_BUTTON", "결제하기 버튼을 눌러주세요.");
        }
    }

    private void RoutePhase11_Payment(int entity)
    {
        // Note: 의도된 단일 처리 영역 (관심사 분리)
        // 결제 세부 단계(카드 삽입, 승인 대기 등)의 피드백은 하드웨어 결제 단말기에 위임함.
        // FSM은 결제 모듈 위치 안내만 수행하며, 결제 완료 여부는 Loop Reset 루틴에서 일괄 처리함.
        // TODO: 향후 비전 레이어에서 결제 진행 상태까지 10-bit 마커로 송출하도록 스펙이 확장될 경우 여기서 entity 분기 처리.
        
        DispatchGuidance("PAYMENT_MODULE_AREA", "마지막으로 결제 수단을 선택해주세요.");
    }

    private void DispatchGuidance(string locationKey, string ttsMessage, bool isException = false)
    {
        if (arManager != null)
        {
            arManager.RenderGlowRing(locationKey);
            if (isException) arManager.TriggerWarningEffect();
        }

        if (ttsManager != null)
        {
            ttsManager.Speak(ttsMessage);
        }
    }

    private void HandleOrderCompleted()
    {
        if (arManager != null) arManager.RenderSuccessFX();
        if (ttsManager != null) ttsManager.Speak("주문이 완료되었습니다. 카드를 뽑아주세요.");
    }
}