import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

AppDialog {
    id: control
    
    property var theme
    property string cameraName: ""
    property string cameraUrl: ""
    property string location: ""
    
    signal cameraAdded(string name, string url, string location)
    
    title: "Add Camera"
    width: theme ? theme.dialogWidthM : 500
    dialogContentHeight: theme ? theme.dialogContentHeightM : 400
    theme: control.theme
    
    Column {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingM : 16
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Camera Name"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: nameInput
                width: parent.width
                placeholderText: "Enter camera name"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Camera URL"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: urlInput
                width: parent.width
                placeholderText: "rtsp://example.com/stream"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Location"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: locationInput
                width: parent.width
                placeholderText: "Enter location"
                theme: control.theme
            }
        }
        
        Item {
            width: parent.width
            height: parent.height - nameInput.height - urlInput.height - locationInput.height - parent.spacing * 4
        }
        
        Row {
            anchors.right: parent.right
            spacing: theme ? theme.spacingS : 8
            
            AppButton {
                text: "Cancel"
                backgroundColor: theme ? theme.surface : "#2d2d2d"
                theme: control.theme
                onClicked: control.close()
            }
            
            AppButton {
                text: "Add Camera"
                backgroundColor: theme ? theme.primary : "#0078d4"
                theme: control.theme
                onClicked: {
                    if (nameInput.text && urlInput.text) {
                        control.cameraAdded(nameInput.text, urlInput.text, locationInput.text)
                        control.close()
                    }
                }
            }
        }
    }
}
