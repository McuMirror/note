package net.macdidi.material01;

import android.os.Build;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.transition.Explode;
import android.transition.Transition;
import android.widget.ImageView;
import android.widget.LinearLayout;

public class ApiLevelExplodeActivity extends AppCompatActivity
{

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        // 如果裝置是 LOLLIPOP 或更新的版本
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            // 設定使用轉換效果
            getWindow().requestFeature(
                android.view.Window.FEATURE_CONTENT_TRANSITIONS);
            // 建立 Explode 轉換效果物件
            Transition explode = new Explode();
            // 設定進入與離開的轉換效果
            getWindow().setEnterTransition(explode);
            getWindow().setExitTransition(explode);
        }

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_api_level);

        // 建立與設定顯示圖片的畫面配置元件
        LinearLayout container = (LinearLayout) findViewById(R.id.container);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.MATCH_PARENT);
        params.setMargins(6, 6, 6, 6);

        // 加入所有圖形元件
        for (int resId : Material01Activity.IMAGE_ARRAY) {
            ImageView image = new ImageView(this);
            image.setImageResource(resId);
            container.addView(image, params);
        }
    }

}
