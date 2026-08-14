import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

AppDialog {
    id: control
    
    property var theme
    property string exportType: "evidence" // evidence, report, logs
    property string startDate: ""
    property string endDate: ""
    property string format: "mp4" // mp4, avi, json, csv
    
    signal exportRequested(string type, string startDate, string endDate, string format)
    
    title: "Export"
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
                text: "Export Type"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppComboBox {
                id: typeInput
                width: parent.width
                theme: control.theme
                model: ["Evidence", "Report", "Logs"]
                currentIndex: 0
                onCurrentTextChanged: {
                    control.exportType = currentText.toLowerCase()
                }
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Start Date"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: startDateInput
                width: parent.width
                placeholderText: "YYYY-MM-DD"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "End Date"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: endDateInput
                width: parent.width
                placeholderText: "YYYY-MM-DD"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Format"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppComboBox {
                id: formatInput
                width: parent.width
                theme: control.theme
                model: control.exportType === "evidence" ? ["MP4", "AVI"] : (control.exportType === "logs" ? ["JSON", "CSV"] : ["PDF", "JSON"])
                currentIndex: 0
                onCurrentTextChanged: {
                    control.format = currentText.toLowerCase()
                }
            }
        }
        
        Item {
            width: parent.width
            height: parent.height - typeInput.height - startDateInput.height - endDateInput.height - formatInput.height - parent.spacing * 4
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
                text: "Export"
                backgroundColor: theme ? theme.primary : "#0078d4"
                theme: control.theme
                onClicked: {
                    control.state = "loading"
                    // Simulate export process
                    Qt.callLater(function() {
                        control.exportRequested(control.exportType, startDateInput.text, endDateInput.text, control.format)
                        control.state = "success"
                        Qt.callLater(function() {
                            control.close()
                        }, 1500)
                    })
                }
            }
        }
    }
}
