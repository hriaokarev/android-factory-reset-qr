plugins {
    id("com.android.application")
}

android {
    namespace = "jp.factoryreset.adbdpc"
    compileSdk = 34

    defaultConfig {
        applicationId = "jp.factoryreset.adbdpc"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    // 依存ゼロ（フレームワークのみ）でビルド安定化
}
