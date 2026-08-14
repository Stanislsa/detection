import QtQuick 2.15
import "."

QtObject {
    property Colors colors: Colors {}
    property Typography typography: Typography {}
    property Dimensions dimensions: Dimensions {}
    property Icons icons: Icons {}

    // ---- Color shortcuts ----
    readonly property string background:        colors.background
    readonly property string backgroundAlt:     colors.backgroundAlt
    readonly property string surface:           colors.surface
    readonly property string surfaceAlt:        colors.surfaceAlt
    readonly property string surfaceElevated:   colors.surfaceElevated
    readonly property string border:            colors.border
    readonly property string borderStrong:      colors.borderStrong
    readonly property string borderFocus:       colors.borderFocus
    readonly property string primary:           colors.primary
    readonly property string primaryHover:      colors.primaryHover
    readonly property string primaryPressed:    colors.primaryPressed
    readonly property string textPrimary:       colors.textPrimary
    readonly property string textSecondary:     colors.textSecondary
    readonly property string textMuted:         colors.textMuted
    readonly property string textDisabled:      colors.textDisabled
    readonly property string success:           colors.success
    readonly property string successHover:     colors.successHover
    readonly property string warning:           colors.warning
    readonly property string warningHover:      colors.warningHover
    readonly property string danger:            colors.danger
    readonly property string dangerHover:       colors.dangerHover
    readonly property string dangerPressed:     colors.dangerPressed
    readonly property string critical:          colors.critical
    readonly property string criticalHover:     colors.criticalHover
    readonly property string criticalPressed:   colors.criticalPressed
    readonly property string info:              colors.info
    readonly property string infoCyber:         colors.infoCyber

    // ---- Typography shortcuts ----
    readonly property string fontFamily:        typography.fontFamily
    readonly property string fontFamilyMono:    typography.fontFamilyMono
    readonly property int fontSizeXS:           typography.fontSizeXS
    readonly property int fontSizeS:            typography.fontSizeS
    readonly property int fontSizeM:            typography.fontSizeM
    readonly property int fontSizeL:            typography.fontSizeL
    readonly property int fontSizeXL:           typography.fontSizeXL
    readonly property int fontSizeXXL:          typography.fontSizeXXL
    readonly property int fontSizeXXXL:         typography.fontSizeXXXL
    readonly property int fontSizeDisplay:     typography.fontSizeDisplay
    readonly property int weightRegular:        typography.weightRegular
    readonly property int weightMedium:         typography.weightMedium
    readonly property int weightSemiBold:       typography.weightSemiBold
    readonly property int weightBold:           typography.weightBold
    readonly property real letterSpacingS:      typography.letterSpacingS
    readonly property real letterSpacingM:      typography.letterSpacingM
    readonly property real letterSpacingL:      typography.letterSpacingL

    // ---- Dimensions shortcuts ----
    readonly property int sidebarWidth:         dimensions.sidebarWidth
    readonly property int headerHeight:         dimensions.headerHeight
    readonly property int footerStatusHeight:   dimensions.footerStatusHeight
    readonly property int spacingXS:           dimensions.spacingXS
    readonly property int spacingS:            dimensions.spacingS
    readonly property int spacingM:            dimensions.spacingM
    readonly property int spacingL:            dimensions.spacingL
    readonly property int spacingXL:           dimensions.spacingXL
    readonly property int spacingXXL:          dimensions.spacingXXL
    readonly property int radiusS:             dimensions.radiusS
    readonly property int radiusM:             dimensions.radiusM
    readonly property int radiusL:             dimensions.radiusL
    readonly property int radiusXL:            dimensions.radiusXL
    readonly property int iconSizeXS:          dimensions.iconSizeXS
    readonly property int iconSizeS:           dimensions.iconSizeS
    readonly property int iconSizeM:           dimensions.iconSizeM
    readonly property int iconSizeL:           dimensions.iconSizeL
    readonly property int iconSizeXL:          dimensions.iconSizeXL
    readonly property int buttonHeight:        dimensions.buttonHeight
    readonly property int buttonHeightLarge:   dimensions.buttonHeightLarge
    readonly property int inputHeight:         dimensions.inputHeight
    readonly property int avatarSizeS:          dimensions.avatarSizeS
    readonly property int avatarSizeM:         dimensions.avatarSizeM
    readonly property int borderWidth:         dimensions.borderWidth
    readonly property int shadowBlur:          dimensions.shadowBlur
    readonly property int shadowOffsetY:       dimensions.shadowOffsetY
    readonly property real shadowOpacity:      dimensions.shadowOpacity
    readonly property color shadowColor:       dimensions.shadowColor
    readonly property int indicatorSize:       dimensions.indicatorSize

    // ---- Icon shortcuts (used by Sidebar.qml) ----
    readonly property var iconsList: icons
}