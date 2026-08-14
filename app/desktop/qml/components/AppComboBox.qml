import QtQuick 2.15
import QtQuick.Controls 2.15

ComboBox {
    id: control
    
    property var theme
    
    property color backgroundColor: theme ? theme.surface : "#2d2d2d"
    property color borderColor: theme ? theme.border : "#404040"
    property color focusColor: theme ? theme.borderFocus : "#0078d4"
    property color textColor: theme ? theme.textPrimary : "#ffffff"
    property color popupColor: theme ? theme.surfaceElevated : "#3d3d3d"
    property color popupHoverColor: theme ? theme.primary : "#0078d4"
    
    implicitHeight: theme ? theme.inputHeight : 36
    implicitWidth: 200
    
    leftPadding: theme ? theme.spacingM : 16
    rightPadding: theme ? theme.spacingM : 16
    topPadding: 0
    bottomPadding: 0
    
    background: Rectangle {
        implicitWidth: 200
        implicitHeight: theme ? theme.inputHeight : 36
        color: control.backgroundColor
        border.color: control.activeFocus ? control.focusColor : control.borderColor
        border.width: control.activeFocus ? 2 : 1
        radius: theme ? theme.radiusM : 8
        
        Behavior on border.color {
            ColorAnimation { duration: 150 }
        }
        
        Behavior on border.width {
            NumberAnimation { duration: 150 }
        }
    }
    
    contentItem: Text {
        text: control.displayText
        font: control.font
        color: control.enabled ? control.textColor : (theme ? theme.textDisabled : "#606060")
        verticalAlignment: Text.AlignVCenter
        leftPadding: theme ? theme.spacingSM : 8
        rightPadding: theme ? theme.spacingSM : 8
        elide: Text.ElideRight
    }
    
    indicator: Canvas {
        id: canvas
        x: control.width - width - control.rightPadding
        y: control.topPadding + (control.availableHeight - height) / 2
        width: theme ? theme.iconSizeS : 16
        height: theme ? theme.iconSizeS : 16
        
        contextType: "2d"
        
        onPaint: {
            context.reset()
            context.moveTo(0, 0)
            context.lineTo(width, 0)
            context.lineTo(width / 2, height)
            context.closePath()
            context.fillStyle = control.textColor
            context.fill()
        }
    }
    
    delegate: ItemDelegate {
        width: control.width
        height: theme ? theme.inputHeight : 36
        
        contentItem: Text {
            text: control.textRole ? (Array.isArray(control.model) ? modelData[control.textRole] : model[control.textRole]) : modelData
            font: control.font
            color: control.textColor
            verticalAlignment: Text.AlignVCenter
            leftPadding: theme ? theme.spacingM : 16
            rightPadding: theme ? theme.spacingM : 16
            elide: Text.ElideRight
        }
        
        background: Rectangle {
            color: control.highlightedIndex === index ? control.popupHoverColor : "transparent"
            radius: theme ? theme.radiusM : 8
        }
    }
    
    popup: Popup {
        y: control.height
        width: control.width
        height: Math.min(contentItem.implicitHeight, control.Window.height - topMargin - bottomMargin)
        implicitHeight: contentItem.implicitHeight
        padding: theme ? theme.spacingXS : 4
        
        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex
            
            ScrollIndicator.vertical: ScrollIndicator { }
        }
        
        background: Rectangle {
            color: control.popupColor
            border.color: control.borderColor
            border.width: 1
            radius: theme ? theme.radiusM : 8
        }
    }
}
