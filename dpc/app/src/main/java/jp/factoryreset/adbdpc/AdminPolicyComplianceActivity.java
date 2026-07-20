package jp.factoryreset.adbdpc;

import android.app.Activity;
import android.os.Bundle;

/**
 * Called after Device Owner is granted. Enable ADB then finish provisioning UI.
 */
public class AdminPolicyComplianceActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        AdbEnabler.enable(this);
        setResult(RESULT_OK);
        finish();
    }
}
