package jp.factoryreset.adbdpc;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

/**
 * Trigger factory reset from PC:
 *   adb shell am broadcast -a jp.factoryreset.adbdpc.ACTION_WIPE \
 *     -n jp.factoryreset.adbdpc/.WipeReceiver --ez confirm true
 */
public class WipeReceiver extends BroadcastReceiver {
    private static final String TAG = "AdbDpc";
    public static final String ACTION_WIPE = "jp.factoryreset.adbdpc.ACTION_WIPE";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null || !ACTION_WIPE.equals(intent.getAction())) {
            return;
        }
        if (!intent.getBooleanExtra("confirm", false)) {
            Log.w(TAG, "WipeReceiver: confirm=false — ignored");
            return;
        }
        Log.i(TAG, "WipeReceiver: confirmed wipe");
        AdbEnabler.wipe(context);
    }
}
