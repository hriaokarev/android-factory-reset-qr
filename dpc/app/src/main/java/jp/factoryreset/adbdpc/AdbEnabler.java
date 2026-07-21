package jp.factoryreset.adbdpc;

import android.app.admin.DevicePolicyManager;
import android.content.ComponentName;
import android.content.Context;
import android.provider.Settings;
import android.util.Log;

public final class AdbEnabler {
    private static final String TAG = "AdbDpc";
    /** PC orchestrator polls this via: adb shell settings get global adbdpc_ready */
    public static final String READY_SETTING = "adbdpc_ready";

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
            dpm.setGlobalSetting(admin, "stay_on_while_plugged_in", "7");
            // Custom marker for automation (may be ignored on some OEMs; package check is fallback)
            try {
                dpm.setGlobalSetting(admin, READY_SETTING, "1");
            } catch (SecurityException ignored) {
                Log.w(TAG, "Could not set " + READY_SETTING + " via DPM; package check still works");
            }
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

    /** Factory reset. Requires Device Owner. */
    public static boolean wipe(Context context) {
        DevicePolicyManager dpm =
                (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
        ComponentName admin = new ComponentName(context, AdbDeviceAdminReceiver.class);
        if (dpm == null || !dpm.isDeviceOwnerApp(context.getPackageName())) {
            Log.w(TAG, "Not device owner; cannot wipe");
            return false;
        }
        try {
            try {
                dpm.setGlobalSetting(admin, READY_SETTING, "0");
            } catch (SecurityException ignored) {
                // ignore
            }
            Log.i(TAG, "Calling wipeData()");
            dpm.wipeData(0);
            return true;
        } catch (SecurityException e) {
            Log.e(TAG, "wipeData failed", e);
            return false;
        }
    }
}
