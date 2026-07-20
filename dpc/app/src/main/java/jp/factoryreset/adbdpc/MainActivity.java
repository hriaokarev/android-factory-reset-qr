package jp.factoryreset.adbdpc;

import android.app.Activity;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        boolean ok = AdbEnabler.enable(this);
        boolean owner = AdbEnabler.isDeviceOwner(this);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int pad = (int) (24 * getResources().getDisplayMetrics().density);
        root.setPadding(pad, pad, pad, pad);

        TextView title = new TextView(this);
        title.setTextSize(22);
        title.setText("ADB Owner");
        root.addView(title);

        TextView status = new TextView(this);
        status.setTextSize(16);
        status.setPadding(0, pad, 0, 0);
        status.setText(
                "Device Owner: " + (owner ? "YES" : "NO") + "\n"
                        + "USB debugging: " + (ok ? "ON" : "failed / not owner"));
        root.addView(status);

        TextView hint = new TextView(this);
        hint.setTextSize(14);
        hint.setPadding(0, pad, 0, 0);
        hint.setText(
                "QRプロビジョニング後に自動でUSBデバッグがONになります。\n"
                        + "起動時にも再適用します。");
        root.addView(hint);

        setContentView(root);
    }
}
