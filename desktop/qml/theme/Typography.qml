import QtQuick 2.15

QtObject {
    // ============================================================
    // SentinelAI — Typography tokens
    // UI text uses `fontFamily` (sans-serif), IDs/logs/metrics
    // use `fontFamilyMono` (monospace). Both have Windows-safe
    // fallback chains; see Fonts.qml for FontLoader declarations.
    // ============================================================

    // ---- Families ----
    readonly property string fontFamily:        "Inter, 'Plus Jakarta Sans', 'Segoe UI', sans-serif"
    readonly property string fontFamilyMono:    "JetBrains Mono, 'Fira Code', 'Cascadia Mono', Consolas, monospace"
    // Alias used by pages that label technical/code values distinctly from `fontFamilyMono`
    readonly property string fontFamilyCode:    fontFamilyMono

    // ---- Sizes ----
    readonly property int fontSizeXS:           11
    readonly property int fontSizeS:            12
    readonly property int fontSizeM:            13
    readonly property int fontSizeL:            14
    readonly property int fontSizeXL:           16
    readonly property int fontSizeXXL:          20
    readonly property int fontSizeXXXL:         28
    readonly property int fontSizeDisplay:      40

    // ---- Weights ----
    readonly property int weightRegular:        Font.Normal     // 400
    readonly property int weightMedium:         Font.Medium     // 500
    readonly property int weightSemiBold:       Font.DemiBold   // 600
    readonly property int weightBold:           Font.Bold       // 700

    // ---- Letter spacing (em) ----
    readonly property real letterSpacingTight:  0
    readonly property real letterSpacingS:      0.02
    readonly property real letterSpacingM:      0.04
    readonly property real letterSpacingL:      0.08

    // ---- Style presets (read by components) ----
    readonly property var pageTitle: {
        "size": fontSizeXXL,
        "weight": weightBold,
        "color": "textPrimary",
        "family": fontFamily,
        "capitalization": Font.MixedCase
    }
    readonly property var sectionTitle: {
        "size": fontSizeL,
        "weight": weightSemiBold,
        "family": fontFamily,
        "color": "textPrimary",
        "capitalization": Font.MixedCase
    }
    readonly property var cardTitle: {
        "size": fontSizeM,
        "weight": weightSemiBold,
        "family": fontFamily,
        "color": "textPrimary",
        "capitalization": Font.MixedCase
    }
    readonly property var body: {
        "size": fontSizeM,
        "weight": weightRegular,
        "family": fontFamily,
        "color": "textPrimary",
        "capitalization": Font.MixedCase
    }
    readonly property var caption: {
        "size": fontSizeXS,
        "weight": weightRegular,
        "family": fontFamily,
        "color": "textSecondary",
        "capitalization": Font.MixedCase
    }
    readonly property var label: {
        "size": fontSizeXS,
        "weight": weightMedium,
        "family": fontFamily,
        "color": "textSecondary",
        "spacing": letterSpacingM,
        "capitalization": Font.AllUppercase
    }
    readonly property var badge: {
        "size": fontSizeXS,
        "weight": weightSemiBold,
        "family": fontFamilyMono,
        "color": "textPrimary",
        "spacing": letterSpacingM,
        "capitalization": Font.AllUppercase
    }
    readonly property var avatarInitials: {
        "size": fontSizeL,
        "weight": weightSemiBold,
        "family": fontFamily,
        "color": "textPrimary",
        "capitalization": Font.AllUppercase
    }
    readonly property var statusBadge: {
        "size": fontSizeXS,
        "weight": weightSemiBold,
        "family": fontFamilyMono,
        "color": "textPrimary",
        "spacing": letterSpacingM,
        "capitalization": Font.AllUppercase
    }
    readonly property var mono: {
        "family": fontFamilyMono,
        "size": fontSizeS,
        "weight": weightRegular,
        "color": "textPrimary"
    }
}