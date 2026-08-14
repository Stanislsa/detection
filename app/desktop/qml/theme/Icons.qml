import QtQuick 2.15

QtObject {
    // ============================================================
    // SentinelAI — Icon glyph registry
    // Returns icon names for use with AppIcon component
    // ============================================================

    // ---- Navigation (matches the 9-item spec sidebar) ----
    readonly property string dashboard:        "layoutDashboard"
    readonly property string cameras:          "camera"
    readonly property string alerts:           "bell"
    readonly property string events:           "calendar"
    readonly property string users:            "users"
    readonly property string aiTraining:       "bot"
    readonly property string observability:    "activity"
    readonly property string systemHealth:     "heartPulse"
    readonly property string settings:         "settings"

    // ---- Status ----
    readonly property string success:          "check"
    readonly property string warning:          "zap"
    readonly property string danger:           "x"
    readonly property string info:             "info"
    readonly property string offline:          "wifiOff"
    readonly property string unknown:          "circleDot"
    readonly property string inactive:         "circleDot"
    readonly property string pending:          "moreHorizontal"

    // ---- Actions ----
    readonly property string play:             "play"
    readonly property string pause:            "pause"
    readonly property string mute:             "volumeX"
    readonly property string unmute:           "volume2"
    readonly property string check:            "check"
    readonly property string close:            "x"
    readonly property string deleteIcon:       "trash2"
    readonly property string edit:             "pencil"
    readonly property string save:             "save"
    readonly property string refresh:          "rotateCw"
    readonly property string search:           "search"
    readonly property string filter:           "slash"
    readonly property string add:              "plus"
    readonly property string removeIcon:       "minus"

    // ---- Categories ----
    readonly property string ai:               "bot"
    readonly property string storage:          "hardDrive"
    readonly property string security:         "shield"
    readonly property string camera:           "camera"
    readonly property string video:            "video"
    readonly property string target:           "target"
    readonly property string mail:             "mail"
    readonly property string inbox:            "inbox"
    readonly property string lightning:        "zap"
    readonly property string person:           "user"
    readonly property string people:           "users"

    // ---- Empty / placeholder ----
    readonly property string empty:            "circleDot"
    readonly property string noData:           "circleDot"
    readonly property string noCamera:         "camera"

    // ---- Glyph aliases for backward compatibility ----
    readonly property string alertGlyph:       "bell"
    readonly property string aiTrainingGlyph:  "bot"
    readonly property string observabilityGlyph: "activity"
    readonly property string eventsGlyph:      "calendar"
    readonly property string successGlyph:     "check"
}