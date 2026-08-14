import QtQuick 2.15

QtObject {
    // ============================================================
    // SentinelAI — Dual Theme Color Tokens (Dark + Light)
    // Components must NEVER hard-code colors — read from `theme.*`.
    // ============================================================

    property bool isDark: true

    // ---- Backgrounds ----
    readonly property string background:        isDark ? "#0B0E14" : "#F1F5F9"
    readonly property string backgroundAlt:     isDark ? "#0F172A" : "#E2E8F0"
    readonly property string surface:           isDark ? "#151C28" : "#FFFFFF"
    readonly property string surfaceAlt:        isDark ? "#1B2433" : "#F8FAFC"
    readonly property string surfaceElevated:   isDark ? "#1E293B" : "#FFFFFF"

    // ---- Borders ----
    readonly property string border:            isDark ? "#1E293B" : "#E2E8F0"
    readonly property string borderStrong:      isDark ? "#334155" : "#CBD5E1"
    readonly property string borderFocus:       "#2563EB"

    // ---- Text ----
    readonly property string textPrimary:       isDark ? "#E5E7EB" : "#0F172A"
    readonly property string textSecondary:     isDark ? "#94A3B8" : "#475569"
    readonly property string textMuted:         isDark ? "#64748B" : "#64748B"
    readonly property string textDisabled:      isDark ? "#475569" : "#94A3B8"

    // ---- Primary (Electric Royal Blue) ----
    readonly property string primary:           "#2563EB"
    readonly property string primaryHover:      "#3B82F6"
    readonly property string primaryPressed:    "#1D4ED8"

    // ---- Semantic accents ----
    readonly property string critical:          "#EF4444"
    readonly property string criticalHover:     "#F87171"
    readonly property string criticalPressed:   "#DC2626"

    readonly property string warning:           "#F59E0B"
    readonly property string warningHover:      "#FBBF24"

    readonly property string success:           "#10B981"
    readonly property string successHover:      "#34D399"

    readonly property string info:              "#06B6D4"
    readonly property string infoCyber:         "#22D3EE"

    // ---- Aliases ----
    readonly property string danger:            critical
    readonly property string dangerHover:       criticalHover
    readonly property string dangerPressed:     criticalPressed

    readonly property string onAccent:          "#FFFFFF"
    readonly property string videoSurface:      "#000000"

    // ---- Overlay / glass ----
    readonly property string overlay:           isDark ? "#00000099" : "#0F172A66"
    readonly property string glass:             isDark ? "#151C28CC" : "#FFFFFFE6"
}
