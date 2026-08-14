import QtQuick 2.15

/*
 * Fonts.qml — FontLoader declarations for SentinelAI.
 *
 * Bundled assets:
 *   - assets/fonts/Inter-Regular.ttf
 *   - assets/fonts/Inter-SemiBold.ttf
 *   - assets/fonts/Inter-Bold.ttf
 *   - assets/fonts/JetBrainsMono-Regular.ttf
 *   - assets/fonts/JetBrainsMono-Bold.ttf
 *
 * If a TTF is absent from disk, FontLoader silently fails and Qt
 * falls back to the next family in the CSS chain defined in
 * Typography.qml (`fontFamily`/`fontFamilyMono`). This keeps the
 * app renderable on any Windows install even before we ship the
 * font binaries.
 */
QtObject {
    readonly property string assetsDir: "../assets/fonts"

    FontLoader { id: interRegular;  source: assetsDir + "/Inter-Regular.ttf"  }
    FontLoader { id: interSemiBold; source: assetsDir + "/Inter-SemiBold.ttf" }
    FontLoader { id: interBold;     source: assetsDir + "/Inter-Bold.ttf"     }
    FontLoader { id: monoRegular;   source: assetsDir + "/JetBrainsMono-Regular.ttf" }
    FontLoader { id: monoBold;      source: assetsDir + "/JetBrainsMono-Bold.ttf"    }
}