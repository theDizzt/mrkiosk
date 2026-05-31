using UnityEngine;

public class RuntimeStateDebugPrinter : MonoBehaviour
{
    [Header("References")]
    public RuntimeStateReader reader;

    [Header("Print Settings")]
    public float printInterval = 0.5f;

    private float timer = 0f;
    private string lastPrintedState = "";
    private int lastPrintedStateId = -999;

    private void Update()
    {
        if (reader == null)
        {
            return;
        }

        timer += Time.deltaTime;

        if (timer < printInterval)
        {
            return;
        }

        timer = 0f;

        if (reader.CurrentState == null)
        {
            Debug.Log("[RuntimeStateDebug] Waiting for runtime_state.json...");
            return;
        }

        bool valid = reader.CurrentState.valid;
        string fsmState = reader.GetFsmStateName();
        int stateId = reader.GetStateMarkerId();
        Vector2 target = reader.GetTargetPosition();
        Vector3 tvec = reader.GetReferenceTvec();
        Vector3 rvec = reader.GetReferenceRvec();

        bool changed =
            fsmState != lastPrintedState ||
            stateId != lastPrintedStateId;

        if (!changed)
        {
            return;
        }

        lastPrintedState = fsmState;
        lastPrintedStateId = stateId;

        TargetData targetData = null;

        if (
            reader.CurrentState != null &&
            reader.CurrentState.fsm != null &&
            reader.CurrentState.fsm.target != null
        )
        {
            targetData = reader.CurrentState.fsm.target;
        }

        string targetText = "null";

        if (targetData != null)
        {
            targetText =
                "center=(" + targetData.x + ", " + targetData.y + "), " +
                "size=(" + targetData.width + ", " + targetData.height + ")";
        }

        Debug.Log(
            "[RuntimeStateDebug]\n" +
            "valid: " + valid + "\n" +
            "fsm.state: " + fsmState + "\n" +
            "state_marker.id: " + stateId + "\n" +
            "target: " + targetText + "\n" +
            "reference.tvec: " + tvec + "\n" +
            "reference.rvec: " + rvec
        );
    }
}
