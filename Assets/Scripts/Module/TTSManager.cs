using UnityEngine;
using System.Collections;

public class TTSManager : MonoBehaviour
{
    private bool isSpeaking = false; 
    
    [Header("Safety Configuration")]
    [Tooltip("TTS 콜백 누락 시 발화 잠금을 강제 해제할 최대 대기 시간(초)")]
    [SerializeField] private float fallbackTimeout = 5.0f;

    public void Speak(string textMessage)
    {
        // 발화 중 재호출 차단 (인터럽트 방어)
        if (isSpeaking) 
        {
            Debug.Log($"[TTS 인터페이스 차단] 발화 중 무시됨: {textMessage}");
            return;
        }

        isSpeaking = true;
        Debug.Log($"[TTS 인터페이스 수신] 오디오 출력 지시: {textMessage}");
        
        // 데드락 방지용 타임아웃 코루틴 실행
        StartCoroutine(SafetyUnlockRoutine());
        
        // TODO: 실제 TTS 연동 시, 발화 종료 콜백에서 isSpeaking = false; 를 호출하고 StopAllCoroutines()를 실행할 것.
    }
    
    /// <summary>
    /// 외부 콜백 누락 시 시스템 먹통을 방지하는 안전망 코루틴
    /// </summary>
    private IEnumerator SafetyUnlockRoutine()
    {
        yield return new WaitForSeconds(fallbackTimeout);
        
        if (isSpeaking)
        {
            Debug.LogWarning("[TTS 안전망 작동] 콜백 반환 시간 초과. 발화 잠금을 강제 해제합니다.");
            isSpeaking = false;
        }
    }
    
    /// <summary>
    /// 강제 중지 및 상태 초기화용 인터페이스
    /// </summary>
    public void StopAndReset()
    {
        isSpeaking = false;
        StopAllCoroutines(); // 진행 중인 타임아웃 타이머도 함께 정지
        // TODO: 실제 TTS 모듈의 Stop() API 호출 로직 추가
    }
}