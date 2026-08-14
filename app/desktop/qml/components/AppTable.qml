import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/*
 * AppTable — fixed: define `alternateRowColor` as a real property
 * (the previous code referenced `theme.surfaceSecondary`, which
 * didn't exist). Apply selection highlight to the active row.
 */
ScrollView {
    id: control

    property var theme
    property var model: []
    property var columns: []
    property color backgroundColor: theme ? theme.background : "#0B0E14"
    property color headerColor: theme ? theme.surface : "#151C28"
    property color rowColor: theme ? theme.surface : "#151C28"
    property color alternateRowColor: theme ? theme.surfaceAlt : "#1B2433"
    property color hoverColor: theme ? theme.surfaceElevated : "#1E293B"
    property color selectedColor: theme ? theme.primary : "#2563EB"
    property color borderColor: theme ? theme.border : "#1E293B"
    property color textColor: theme ? theme.textPrimary : "#E5E7EB"
    property color headerTextColor: theme ? theme.textSecondary : "#94A3B8"

    clip: true

    ListView {
        id: listView
        model: control.model
        spacing: 0
        boundsBehavior: Flickable.StopAtBounds

        property int activeIndex: -1
        onCurrentIndexChanged: activeIndex = currentIndex

        header: Rectangle {
            width: listView.width
            height: theme ? theme.buttonHeight : 36
            color: control.headerColor
            border.color: control.borderColor
            border.width: 1

            Row {
                anchors.fill: parent
                spacing: 0

                Repeater {
                    model: control.columns

                    delegate: Rectangle {
                        width: modelData.width || 100
                        height: parent.height
                        color: "transparent"

                        Text {
                            anchors.fill: parent
                            text: modelData.title || ""
                            font.family: theme ? theme.fontFamilyMono : "Consolas"
                            font.pixelSize: theme ? theme.fontSizeXS : 11
                            font.letterSpacing: theme ? theme.letterSpacingM : 0.04
                            font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                            color: control.headerTextColor
                            horizontalAlignment: modelData.alignment || Text.AlignLeft
                            verticalAlignment: Text.AlignVCenter
                            leftPadding: theme ? theme.spacingS : 8
                            rightPadding: theme ? theme.spacingS : 8
                            elide: Text.ElideRight
                        }

                        Rectangle {
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: 1
                            color: control.borderColor
                        }
                    }
                }
            }
        }

        delegate: Rectangle {
            width: listView.width
            height: theme ? theme.buttonHeight : 36
            color: listView.activeIndex === index
                ? Qt.darker(control.selectedColor, 4)
                : (index % 2 === 0 ? control.rowColor : control.alternateRowColor)
            border.color: control.borderColor
            border.width: 1

            Behavior on color { ColorAnimation { duration: 100 } }

            Row {
                anchors.fill: parent
                spacing: 0

                Repeater {
                    model: control.columns

                    delegate: Rectangle {
                        width: modelData.width || 100
                        height: parent.height
                        color: "transparent"

                        Text {
                            anchors.fill: parent
                            text: {
                                var value = modelData.field ? modelData[modelData.field] : modelData[index]
                                if (modelData.format) return modelData.format(value)
                                return value !== undefined ? value.toString() : ""
                            }
                            font.family: modelData.mono && theme ? theme.fontFamilyMono : (theme ? theme.fontFamily : "Inter")
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            color: control.textColor
                            horizontalAlignment: modelData.alignment || Text.AlignLeft
                            verticalAlignment: Text.AlignVCenter
                            leftPadding: theme ? theme.spacingS : 8
                            rightPadding: theme ? theme.spacingS : 8
                            elide: Text.ElideRight
                        }

                        Rectangle {
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: 1
                            color: control.borderColor
                        }

                        // 8px status strip on the leading cell
                        Rectangle {
                            visible: index === 0 && modelData.statusField
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: 4
                            color: {
                                if (!modelData.statusField) return "transparent"
                                var v = modelData.statusField(modelData[modelData.statusField])
                                if (v === "high" || v === "critical") return theme ? theme.critical : "#EF4444"
                                if (v === "medium" || v === "warning") return theme ? theme.warning : "#F59E0B"
                                if (v === "low") return theme ? theme.info : "#06B6D4"
                                return theme ? theme.success : "#10B981"
                            }
                        }
                    }
                }
            }

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onEntered: if (listView.activeIndex !== index) parent.color = control.hoverColor
                onExited: parent.color = listView.activeIndex === index
                    ? Qt.darker(control.selectedColor, 4)
                    : (index % 2 === 0 ? control.rowColor : control.alternateRowColor)
                onClicked: listView.currentIndex = index
            }
        }
    }

    background: Rectangle {
        color: control.backgroundColor
        border.color: control.borderColor
        border.width: theme ? theme.borderWidth : 1
        radius: theme ? theme.radiusM : 4
    }
}