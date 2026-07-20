package jp.factoryreset.adbdpc;

import android.app.admin.DevicePolicyManager;
import android.content.ComponentName;
import android.content.Context;
import android.provider.Settings;
import android.util.Log;

public final class AdbEnabler {
    private static final String TAG = "AdbDpc";

    private AdbEnabler() {}

    public static boolean enable(Context context) {
        DevicePolicyManager dpm =
                (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
        ComponentName admin = new ComponentName(context, AdbDeviceAdminReceiver.class);

        if (dpm == null || !dpm.isDeviceOwnerApp(context.getPackageName())) {
            Log.w(TAG, "Not device owner; cannot enable ADB");
            return false;
        }

        try {
            dpm.setGlobalSetting(admin, Settings.Global.DEVELOPMENT_SETTINGS_ENABLED, "1");
            dpm.setGlobalSetting(admin, Settings.Global.ADB_ENABLED, "1");
            // Stay awake while charging (optional convenience)
            dpm.setGlobalSetting(admin, "stay_on_while_plugged_in", "7");
            Log.i(TAG, "USB debugging enabled");
            return true;
        } catch (SecurityException e) {
            Log.e(TAG, "Failed to enable ADB", e);
            return false;
        }
    }

    public static boolean isDeviceOwner(Context context) {
        DevicePolicyManager dpm =
                (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
        return dpm != null && dpm.isDeviceOwnerApp(context.getPackageName());
    }
}
