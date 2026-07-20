package jp.factoryreset.adbdpc;

import android.app.Activity;
import android.app.admin.DevicePolicyManager;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;

/**
 * Required on Android 12+: tell ManagedProvisioning we want fully managed (Device Owner).
 */
public class GetProvisioningModeActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Intent result = new Intent();
        if (Build.VERSION.SDK_INT >= 29) {
            result.putExtra(
                    DevicePolicyManager.EXTRA_PROVISIONING_MODE,
                    DevicePolicyManager.PROVISIONING_MODE_FULLY_MANAGED_DEVICE);
        } else {
            // Fallback constant value = 1 (fully managed)
            result.putExtra("android.app.extra.PROVISIONING_MODE", 1);
        }
        setResult(RESULT_OK, result);
        finish();
    }
}
