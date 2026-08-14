import QtQuick 2.15

QtObject {
    // ============================================================
    // SentinelAI — Cyber-Security / Sci-Fi Industrial Palette
    // Single source of truth for color tokens.
    // Components must NEVER hard-code colors — read from `theme.*`.
    // ============================================================

    // ---- Backgrounds (Deep Slate / Navy) ----
    readonly property string background:        "#0B0E14"
    readonly property string backgroundAlt:     "#0F172A"
    readonly property string surface:           "#151C28"
    readonly property string surfaceAlt:        "#1B2433"
    readonly property string surfaceElevated:   "#1E293B"

    // ---- Borders (1px, subtle) ----
    readonly property string border:            "#1E293B"
    readonly property string borderStrong:      "#334155"
    readonly property string borderFocus:       "#2563EB"

    // ---- Text ----
    readonly property string textPrimary:       "#E5E7EB"
    readonly property string textSecondary:     "#94A3B8"
    readonly property string textMuted:         "#64748B"
    readonly property string textDisabled:      "#475569"

    // ---- Primary (Electric Royal Blue) ----
    readonly property string primary:           "#2563EB"
    readonly property string primaryHover:      "#3B82F6"
    readonly property string primaryPressed:    "#1D4ED8"

    // ---- Semantic accents ----
    // Critical / Danger / Error
    readonly property string critical:          "#EF4444"
    readonly property string criticalHover:     "#F87171"
    readonly property string criticalPressed:   "#DC2626"

    // Warning / Amber
    readonly property string warning:           "#F59E0B"
    readonly property string warningHover:      "#FBBF24"

    // Success / Online (Emerald)
    readonly property string success:           "#10B981"
    readonly property string successHover:      "#34D399"

    // Info (Cyan / Ice Blue)
    readonly property string info:              "#06B6D4"
    readonly property string infoCyber:         "#22D3EE"

    // ---- Aliases (back-compat with existing component code) ----
    readonly property string danger:            critical
    readonly property string dangerHover:       criticalHover
    readonly property string dangerPressed:     criticalPressed
}