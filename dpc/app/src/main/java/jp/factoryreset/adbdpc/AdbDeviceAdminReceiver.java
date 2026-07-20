package jp.factoryreset.adbdpc;

import android.app.admin.DeviceAdminReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

public class AdbDeviceAdminReceiver extends DeviceAdminReceiver {
    private static final String TAG = "AdbDpc";

    @Override
    public void onEnabled(Context context, Intent intent) {
        Log.i(TAG, "Device admin enabled");
        AdbEnabler.enable(context);
    }

    @Override
    public void onProfileProvisioningComplete(Context context, Intent intent) {
        Log.i(TAG, "Provisioning complete");
        AdbEnabler.enable(context);
    }
}
