package jp.factoryreset.adbdpc;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;

/**
 * Optional wipe entry:
 *   adb shell am start -n jp.factoryreset.adbdpc/.WipeActivity --ez confirm true
 */
public class WipeActivity extends Activity {
    private static final String TAG = "AdbDpc";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        boolean confirm = getIntent() != null && getIntent().getBooleanExtra("confirm", false);
        if (!confirm) {
            Toast.makeText(this, "Wipe requires --ez confirm true", Toast.LENGTH_LONG).show();
            finish();
            return;
        }
        Log.i(TAG, "WipeActivity: wiping");
        boolean ok = AdbEnabler.wipe(this);
        if (!ok) {
            Toast.makeText(this, "Wipe failed (not device owner?)", Toast.LENGTH_LONG).show();
        }
        finish();
    }
}
