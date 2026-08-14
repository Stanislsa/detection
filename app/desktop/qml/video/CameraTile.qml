import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

Rectangle {
    id: control
    
    property var theme
    property string cameraName: "Camera 1"
    property string cameraId: ""
    property bool isOnline: true
    property bool hasAlert: false
    property real alertLevel: 0 // 0-1
    
    signal clicked()
    signal settingsClicked()
    
    implicitWidth: theme ? theme.cameraTileWidth : 320
    implicitHeight: theme ? theme.cameraTileHeight : 240
    
    color: theme ? theme.surface : "#2d2d2d"
    radius: theme ? theme.radiusM : 8
    border.color: hasAlert ? (theme ? theme.danger : "#d13438") : (theme ? theme.border : "#404040")
    border.width: hasAlert ? 2 : 1
    
    scale: control.hovered ? 1.02 : 1
    
    Behavior on scale {
        NumberAnimation { duration: 150; easing.type: Easing.InOutQuad }
    }
    
    Column {
        anchors.fill: parent
        spacing: theme ? theme.spacingXS : 0
        
        // Video preview
        Rectangle {
            width: parent.width
            height: parent.height - 50
            color: theme ? theme.surfaceElevated : "#3d3d3d"
            
            Text {
                anchors.centerIn: parent
                text: "📷"
                font.pixelSize: theme ? theme.fontSizeXXXL : 32
                color: theme ? theme.textDisabled : "#606060"
            }
            
            // Alert indicator
            Rectangle {
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: theme ? theme.spacingS : 8
                width: theme ? theme.indicatorSize : 12
                height: theme ? theme.indicatorSize : 12
                radius: theme ? theme.indicatorSize / 2 : 6
                color: hasAlert ? (theme ? theme.danger : "#d13438") : (theme ? theme.success : "#107c10")
                visible: true
            }
            
            // Alert level bar
            Rectangle {
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: theme ? theme.indicatorBarHeight : 4
                color: "transparent"
                
                Rectangle {
                    anchors.left: parent.left
                    anchors.bottom: parent.bottom
                    width: parent.width * alertLevel
                    height: parent.height
                    color: theme ? theme.danger : "#d13438"
                    visible: hasAlert
                }
            }
        }
        
        // Info bar
        Rectangle {
            width: parent.width
            height: theme ? theme.cameraInfoBarHeight : 50
            color: theme ? theme.surface : "#2d2d2d"
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: theme ? theme.spacingM : 16
                anchors.rightMargin: theme ? theme.spacingM : 16
                spacing: theme ? theme.spacingS : 8
                
                Text {
                    id: cameraNameText
                    text: cameraName
                    font.pixelSize: theme ? theme.fontSizeM : 14
                    font.bold: true
                    color: theme ? theme.textPrimary : "#ffffff"
                    Layout.alignment: Qt.AlignVCenter
                }
                
                Item {
                    Layout.fillWidth: true
                }
                
                AppIconButton {
                    id: settingsButton
                    text: "⚙️"
                    theme: control.theme
                    Layout.alignment: Qt.AlignVCenter
                    onClicked: control.settingsClicked()
                }
            }
        }
    }
    
    MouseArea {
        anchors.fill: parent
        onClicked: control.clicked()
        hoverEnabled: true
    }
}
