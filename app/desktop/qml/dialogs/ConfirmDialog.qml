import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

AppDialog {
    id: control
    
    property var theme
    property string message: ""
    property string confirmText: "Confirm"
    property string cancelText: "Cancel"
    property bool isDestructive: false
    
    signal confirmed()
    
    title: "Confirm"
    width: theme ? theme.dialogWidthS : 400
    dialogContentHeight: theme ? theme.dialogContentHeightS : 150
    theme: control.theme
    
    Column {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingM : 16
        
        Text {
            width: parent.width
            text: control.message
            font.pixelSize: theme ? theme.fontSizeM : 14
            color: theme ? theme.textPrimary : "#ffffff"
            wrapMode: Text.WordWrap
        }
        
        Item {
            width: parent.width
            height: parent.height - parent.height
        }
        
        Row {
            anchors.right: parent.right
            spacing: theme ? theme.spacingS : 8
            
            AppButton {
                text: control.cancelText
                backgroundColor: theme ? theme.surface : "#2d2d2d"
                theme: control.theme
                onClicked: control.close()
            }
            
            AppButton {
                text: control.confirmText
                backgroundColor: control.isDestructive ? (theme ? theme.danger : "#d13438") : (theme ? theme.primary : "#0078d4")
                theme: control.theme
                onClicked: {
                    control.confirmed()
                    control.close()
                }
            }
        }
    }
}
