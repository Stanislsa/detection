import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

Column {
    id: control
    
    property var theme
    property string title: "No data"
    property string message: "There is nothing to display here"
    property string icon: "📭"
    
    spacing: theme.spacingL
    
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        text: control.icon
        font.pixelSize: theme ? theme.fontSizeDisplay : 48
        opacity: 0.5
    }
    
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        text: control.title
        font.pixelSize: theme.fontSizeXL
        font.bold: true
        color: theme.textSecondary
    }
    
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        text: control.message
        font.pixelSize: theme.fontSizeM
        color: theme.textDisabled
    }
    
    AppButton {
        anchors.horizontalCenter: parent.horizontalCenter
        text: "Refresh"
        theme: control.theme
    }
}
