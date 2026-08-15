import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

AppDialog {
    id: control
    
    property var theme
    property var settingsController
    
    title: "AI & Inference Settings"
    width: 500
    dialogContentHeight: 500
    theme: control.theme
    
    Component.onCompleted: {
        if (settingsController) {
            modelInput.text = settingsController.aiSettings.model_name || "yolov8"
            confidenceInput.text = settingsController.aiSettings.confidence_threshold || 0.5
            nmsInput.text = settingsController.aiSettings.nms_threshold || 0.45
            maxDetectionsInput.text = settingsController.aiSettings.max_detections || 100
            poseCheck.checked = settingsController.aiSettings.enable_pose_estimation !== undefined ? settingsController.aiSettings.enable_pose_estimation : true
            faceCheck.checked = settingsController.aiSettings.enable_face_recognition !== undefined ? settingsController.aiSettings.enable_face_recognition : false
            deviceCombo.currentIndex = deviceCombo.find(settingsController.aiSettings.inference_device || "cpu")
        }
    }
    
    Column {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingM : 16
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Model Name"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: modelInput
                width: parent.width
                placeholderText: "yolov8"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Confidence Threshold"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: confidenceInput
                width: parent.width
                placeholderText: "0.5"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "NMS Threshold"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: nmsInput
                width: parent.width
                placeholderText: "0.45"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Max Detections"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: maxDetectionsInput
                width: parent.width
                placeholderText: "100"
                theme: control.theme
            }
        }
        
        Row {
            spacing: theme ? theme.spacingM : 16
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: poseCheck
                    text: "Pose Estimation"
                    theme: control.theme
                }
                
                Text {
                    text: "Enable pose estimation"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: faceCheck
                    text: "Face Recognition"
                    theme: control.theme
                }
                
                Text {
                    text: "Enable face recognition"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Inference Device"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppComboBox {
                id: deviceCombo
                width: parent.width
                theme: control.theme
                model: ["cpu", "gpu", "tpu"]
                currentIndex: 0
            }
        }
        
        Item {
            width: parent.width
            height: parent.height - modelInput.height - confidenceInput.height - nmsInput.height - maxDetectionsInput.height - deviceCombo.height - parent.spacing * 6
        }
        
        Row {
            anchors.right: parent.right
            spacing: theme ? theme.spacingS : 8
            
            AppButton {
                text: "Cancel"
                variant: "secondary"
                theme: control.theme
                onClicked: control.close()
            }
            
            AppButton {
                text: "Save"
                variant: "primary"
                theme: control.theme
                onClicked: {
                    if (settingsController) {
                        settingsController.updateAISettings(
                            modelInput.text,
                            parseFloat(confidenceInput.text) || 0.5,
                            parseFloat(nmsInput.text) || 0.45,
                            parseInt(maxDetectionsInput.text) || 100,
                            poseCheck.checked,
                            faceCheck.checked,
                            deviceCombo.currentText
                        )
                        control.close()
                    }
                }
            }
        }
    }
}
