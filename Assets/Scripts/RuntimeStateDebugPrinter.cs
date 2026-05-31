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
        Vector3 target = reader.GetTargetWorldPosition();
        Vector2 targetSize = reader.GetTargetWorldSize();
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

        if (
            targetData != null &&
            targetData.world_position != null &&
            targetData.world_size != null
        )
        {
            targetText =
                "world_position=(" +
                targetData.world_position.x + ", " +
                targetData.world_position.y + ", " +
                targetData.world_position.z + "), " +
                "world_size=(" +
                targetData.world_size.w + ", " +
                targetData.world_size.h + ")";
        }

        Debug.Log(
            "[RuntimeStateDebug]\n" +
            "valid: " + valid + "\n" +
            "fsm.state: " + fsmState + "\n" +
            "state_marker.id: " + stateId + "\n" +
            "target: " + targetText + "\n" +
            "reader.targetWorldPosition: " + target + "\n" +
            "reader.targetWorldSize: " + targetSize + "\n" +
            "reference.tvec: " + tvec + "\n" +
            "reference.rvec: " + rvec
        );
    }
}
