package com.gathin.tvhome;

import android.app.Activity;
import android.os.Bundle;
import android.media.tv.TvView;
import android.net.Uri;
import android.graphics.Color;
import android.view.Gravity;
import android.view.WindowManager;
import android.widget.FrameLayout;
import android.widget.TextView;

/** Native HDMI surface for this Insignia; Back returns to the launcher. */
public final class InputActivity extends Activity {
    private TvView video;
    private TextView status;
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.BLACK);
        video = new TvView(this);
        root.addView(video, new FrameLayout.LayoutParams(-1, -1));
        status = new TextView(this);
        status.setText("HDMI · Connecting…");
        status.setTextColor(Color.WHITE);
        status.setTextSize(22);
        status.setPadding(36, 24, 36, 24);
        FrameLayout.LayoutParams label = new FrameLayout.LayoutParams(-2, -2, Gravity.TOP | Gravity.LEFT);
        root.addView(status, label);
        video.setCallback(new TvView.TvInputCallback() {
            @Override public void onVideoAvailable(String id) { status.setVisibility(android.view.View.GONE); }
            @Override public void onVideoUnavailable(String id, int reason) {
                status.setVisibility(android.view.View.VISIBLE);
                status.setText("HDMI · No picture yet. Check that your device is on.  BACK to return.");
            }
            @Override public void onConnectionFailed(String id) {
                status.setText("HDMI unavailable. Use your remote Input button.  BACK to return.");
            }
        });
        setContentView(root);
    }
    @Override public void onResume() {
        super.onResume();
        String id = getIntent().getStringExtra("input_id");
        if (id == null || !id.startsWith("com.mediatek.tis/")) { finish(); return; }
        try { video.tune(id, Uri.EMPTY); video.setStreamVolume(1f); }
        catch (SecurityException | IllegalArgumentException unavailable) {
            status.setText("HDMI unavailable. Use your remote Input button.  BACK to return.");
        }
    }
    @Override public void onPause() { video.reset(); super.onPause(); }
}
