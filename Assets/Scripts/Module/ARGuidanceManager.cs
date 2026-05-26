using UnityEngine;

public class ARGuidanceManager : MonoBehaviour
{
    private string currentLocationKey = string.Empty;

    public void RenderGlowRing(string locationKey)
    {
        // 중복 호출 방어 (멱등성 보장)
        if (this.currentLocationKey == locationKey) return;
        
        this.currentLocationKey = locationKey;
        
        // 비전/오버레이 담당자가 구현할 3D 월드 좌표 매핑 영역
        Debug.Log($"[AR 인터페이스 수신] 위치 키 갱신 및 렌더링: {locationKey}");
    }

    public void TriggerWarningEffect()
    {
        // 경로 예외 발생 시 빨간색 경고 셰이더 적용 영역
        Debug.LogWarning("[AR 인터페이스 수신] 경고 이펙트 트리거");
    }

    public void RenderSuccessFX()
    {
        // 결제 완료 시 이펙트 재생 영역
        Debug.Log("[AR 인터페이스 수신] 주문 성공 파티클 재생");
    }
    
    /// <summary>
    /// 강제 화면 전환 등 렌더링 상태 초기화가 필요할 때 호출
    /// </summary>
    public void ClearState()
    {
        currentLocationKey = string.Empty;
    }
}