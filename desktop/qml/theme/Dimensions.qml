import QtQuick 2.15

QtObject {
    // ============================================================
    // SentinelAI — Dimension / chrome tokens
    // Industrial chrome: 1px borders, 4px radius, shadow-xl.
    // ============================================================

    // ---- Layout ----
    readonly property int sidebarWidth:           240
    readonly property int sidebarCollapsedWidth:  64
    readonly property int headerHeight:           56
    readonly property int footerStatusHeight:     32

    // ---- Spacing scale ----
    readonly property int spacingXS:           4
    readonly property int spacingS:            8
    readonly property int spacingM:            16
    readonly property int spacingL:            24
    readonly property int spacingXL:           32
    readonly property int spacingXXL:          48

    // ---- Radius (industrial chrome = 4) ----
    readonly property int radiusS:             2
    readonly property int radiusM:             4
    readonly property int radiusL:             6
    readonly property int radiusXL:            8

    // ---- Icon sizes ----
    readonly property int iconSizeXS:          12
    readonly property int iconSizeS:           14
    readonly property int iconSizeM:           18
    readonly property int iconSizeL:           22
    readonly property int iconSizeXL:          28

    // ---- Buttons / inputs ----
    readonly property int buttonHeight:        36
    readonly property int buttonHeightLarge:   44
    readonly property int inputHeight:         36

    // ---- Avatars ----
    readonly property int avatarSizeS:         32
    readonly property int avatarSizeM:         64

    // ---- Card heights ----
    readonly property int cardHeightS:         70
    readonly property int cardHeightM:         100
    readonly property int cardHeightL:         150
    readonly property int cardHeightXL:        200
    readonly property int cardHeightXXL:       400

    // ---- Spacing aliases (SM/MD/LG naming used by auth + form pages) ----
    readonly property int spacingSM:           spacingS
    readonly property int spacingMD:           spacingM
    readonly property int spacingLG:           spacingL

    // ---- Table column widths ----
    readonly property int columnWidthS:        150
    readonly property int columnWidthM:        200

    // ---- Login ----
    readonly property int loginCardWidth:      400

    // ---- Border (standardized to 1px) ----
    readonly property int borderWidth:         1

    // ---- Shadows (used with DropShadow layer) ----
    readonly property int shadowBlur:          24
    readonly property int shadowOffsetY:       8
    readonly property real shadowOpacity:      0.25
    readonly property color shadowColor:      "#000000"

    // ---- Dialogs ----
    readonly property int dialogWidth:         500
    readonly property int dialogHeight:        500
    readonly property int dialogWidthS:        400
    readonly property int dialogWidthM:        dialogWidth
    readonly property int dialogContentHeightS: 150
    readonly property int dialogContentHeightM: 400
    readonly property int dialogContentHeightL: 450

    // ---- Video ----
    readonly property int videoWidth:          640
    readonly property int videoHeight:         480
    readonly property int videoControlsHeight: 50
    readonly property int cameraTileWidth:     320
    readonly property int cameraTileHeight:    240
    readonly property int cameraInfoBarHeight: 50

    // ---- Indicators ----
    readonly property int indicatorSize:       8
    readonly property int indicatorBarHeight:  4
}