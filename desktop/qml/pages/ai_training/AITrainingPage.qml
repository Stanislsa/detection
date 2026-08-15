import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

Item {
    id: control
    property var theme
    readonly property bool isNarrow: width < 960
    readonly property bool isMobile: width < 720
    readonly property int pageMargin: isMobile ? 10 : (isNarrow ? 14 : 24)

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingM : 16

        // Active job card
        Rectangle {
            Layout.fillWidth: true; height: 140; radius: 6
            color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"; border.width: 1

            ColumnLayout {
                anchors.fill: parent; anchors.margins: 20; spacing: 10

                RowLayout {
                    Layout.fillWidth: true
                    Rectangle {
                        width: jobId.implicitWidth + 12; height: 20; radius: 4
                        color: theme ? theme.surfaceElevated : "#1E293B"
                        Text { id: jobId; anchors.centerIn: parent; text: "JOB_ID: 8824-A"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    }
                    Text { text: "Sentinel_Vision_v4.2-Final"; font.pixelSize: 16; font.weight: Font.Bold; color: theme ? theme.textPrimary : "#E5E7EB" }
                    Item { Layout.fillWidth: true }
                    AppButton { text: "PARAMS"; variant: "secondary"; theme: control.theme }
                    AppButton { text: "HALT TRAINING"; variant: "danger"; theme: control.theme }
                }
                Text {
                    text: "Executing hyperparameter optimization for anomaly detection in low-light infrared streams. Utilizing dataset: global-perimeter-v9."
                    font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8"
                    Layout.fillWidth: true; wrapMode: Text.WordWrap
                }
                RowLayout {
                    Layout.fillWidth: true; spacing: 24
                    Column {
                        spacing: 4
                        Text { text: "EPOCH PROGRESS"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Row {
                            spacing: 8
                            Rectangle {
                                width: 160; height: 8; radius: 4; color: theme ? theme.backgroundAlt : "#0F172A"
                                Rectangle { width: parent.width * 0.84; height: parent.height; radius: 4; color: theme ? theme.primary : "#2563EB" }
                            }
                            Text { text: "84% (42/50)"; font.pixelSize: 11; color: theme ? theme.textPrimary : "#E5E7EB"; anchors.verticalCenter: parent.verticalCenter }
                        }
                    }
                    Column {
                        spacing: 2
                        Text {
                            text: "ELAPSED TIME"
                            font.pixelSize: 10
                            font.family: theme ? theme.fontFamilyMono : "monospace"
                            color: theme ? theme.textMuted : "#64748B"
                        }
                        Text {
                            text: "04:22:18"
                            font.pixelSize: 14
                            font.family: theme ? theme.fontFamilyMono : "monospace"
                            color: theme ? theme.textPrimary : "#E5E7EB"
                        }
                    }
                    Column {
                        spacing: 2
                        Text {
                            text: "ESTIMATED FINISH"
                            font.pixelSize: 10
                            font.family: theme ? theme.fontFamilyMono : "monospace"
                            color: theme ? theme.textMuted : "#64748B"
                        }
                        Text {
                            text: "~01:45:00"
                            font.pixelSize: 14
                            font.family: theme ? theme.fontFamilyMono : "monospace"
                            color: theme ? theme.textPrimary : "#E5E7EB"
                        }
                    }
                    Column {
                        spacing: 2
                        Text {
                            text: "AVG STEP SPEED"
                            font.pixelSize: 10
                            font.family: theme ? theme.fontFamilyMono : "monospace"
                            color: theme ? theme.textMuted : "#64748B"
                        }
                        Text {
                            text: "142ms/it"
                            font.pixelSize: 14
                            font.family: theme ? theme.fontFamilyMono : "monospace"
                            color: theme ? theme.success : "#10B981"
                        }
                    }
                }
            }
        }

        // Metrics row
        RowLayout {
            Layout.fillWidth: true; spacing: 12
            Repeater {
                model: [
                    { t: "CURRENT LOSS", v: "0.0821", u: "RMS", d: "-12.4% vs last run", up: true },
                    { t: "VALIDATION ACC", v: "98.42", u: "%", d: "+2.1% vs last run", up: true },
                    { t: "LEARNING RATE", v: "1.2e-4", u: "ADAM", d: "", up: true },
                    { t: "BATCH SIZE", v: "128", u: "IMG", d: "", up: true },
                    { t: "GPU THERMALS", v: "72.0", u: "°C", d: "ACTIVE", up: true }
                ]
                Rectangle {
                    Layout.fillWidth: true; height: 90; radius: 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"; border.width: 1
                    Column {
                        anchors.fill: parent; anchors.margins: 12; spacing: 2
                        Text { text: modelData.t; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Row {
                            spacing: 4
                            Text { text: modelData.v; font.pixelSize: 20; font.weight: Font.Bold; color: theme ? theme.textPrimary : "#E5E7EB" }
                            Text { text: modelData.u; font.pixelSize: 11; color: theme ? theme.textMuted : "#64748B"; anchors.bottom: parent.bottom; anchors.bottomMargin: 3 }
                        }
                        Text { text: modelData.d; font.pixelSize: 10; color: modelData.up ? (theme ? theme.success : "#10B981") : (theme ? theme.critical : "#EF4444"); visible: modelData.d !== "" }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 16

            // Training dynamics chart
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 2
                radius: 4; color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"; border.width: 1
                Column {
                    anchors.fill: parent; anchors.margins: 16; spacing: 8
                    RowLayout {
                        width: parent.width
                        Text { text: "Training Dynamics"; font.pixelSize: 14; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                        Item { Layout.fillWidth: true }
                        Text { text: "LOG SCALE: OFF"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { text: "REFRESH: 5s"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    }
                    Canvas {
                        width: parent.width; height: parent.height - 50
                        onPaint: {
                            var ctx = getContext("2d"); ctx.clearRect(0,0,width,height)
                            // accuracy green
                            ctx.strokeStyle = "#10B981"; ctx.lineWidth = 2; ctx.beginPath()
                            var acc = [0.55,0.65,0.72,0.78,0.82,0.86,0.89,0.92,0.94,0.96,0.97,0.98]
                            for (var i=0;i<acc.length;i++){ var x=i/(acc.length-1)*width; var y=height-acc[i]*height; if(i===0)ctx.moveTo(x,y); else ctx.lineTo(x,y) }
                            ctx.stroke()
                            // loss red
                            ctx.strokeStyle = "#EF4444"; ctx.beginPath()
                            var loss = [0.9,0.7,0.55,0.42,0.32,0.25,0.2,0.16,0.13,0.11,0.09,0.08]
                            for (var j=0;j<loss.length;j++){ var x2=j/(loss.length-1)*width; var y2=height-loss[j]*height; if(j===0)ctx.moveTo(x2,y2); else ctx.lineTo(x2,y2) }
                            ctx.stroke()
                        }
                        Component.onCompleted: requestPaint()
                    }
                }
            }

            // System stream log
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 1
                radius: 4; color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"; border.width: 1
                Column {
                    anchors.fill: parent; anchors.margins: 12; spacing: 4
                    Text { text: "System Stream"; font.pixelSize: 13; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                    Flickable {
                        width: parent.width; height: parent.height - 30; clip: true
                        contentHeight: logCol.height
                        Column {
                            id: logCol; width: parent.width; spacing: 3
                            Repeater {
                                model: [
                                    "[14:22:01] INFO  Epoch 42: Optimizer step com",
                                    "[14:22:05] INFO  Loss minimized: 0.0825 → 0.1",
                                    "[14:22:12] INFO  Validation subset 'night_rai",
                                    "[14:22:18] WARN  GPU Memory overhead approach",
                                    "[14:22:25] INFO  Checkpoint saved: periodic_s",
                                    "[14:22:30] INFO  Global step 14,200 reached.",
                                    "[14:22:35] INFO  LR Schedule update: 1.2e-4 (",
                                    "[14:22:42] INFO  Prefetching batch 14,201 fro",
                                    "[14:22:48] INFO  Batch normalization stats up",
                                    "[14:22:55] INFO  Synchronizing weights across",
                                    "[14:23:01] INFO  Epoch 43: Initializing..."
                                ]
                                Text {
                                    text: modelData; width: parent.width
                                    font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"
                                    color: modelData.indexOf("WARN") >= 0 ? "#F59E0B" : (theme ? theme.textSecondary : "#94A3B8")
                                    elide: Text.ElideRight
                                }
                            }
                        }
                    }
                }
            }
        }

        // Recent experiments
        Rectangle {
            Layout.fillWidth: true; Layout.preferredHeight: 160
            radius: 4; color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"; border.width: 1
            clip: true
            ColumnLayout {
                anchors.fill: parent; spacing: 0
                Rectangle {
                    Layout.fillWidth: true; height: 36
                    Text { anchors.left: parent.left; anchors.leftMargin: 16; anchors.verticalCenter: parent.verticalCenter; text: "Recent Training Experiments"; font.pixelSize: 13; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                    AppButton { anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; text: "VIEW FULL REGISTRY"; variant: "ghost"; theme: control.theme }
                }
                ListView {
                    Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                    model: [
                        { job: "ResNet_Detection_PRO", alg: "ResNet-101", ds: "night_surv_v2", rt: "12h 44m", st: "STABLE", met: "mAP: 0.941" },
                        { job: "YOLO_Infrared_EXP_01", alg: "YOLOv8-Custom", ds: "ir_forest_low", rt: "03h 12m", st: "FAILED", met: "GRAD EXPLOSION" },
                        { job: "Anomaly_Unsupervised_v1", alg: "AutoEncoder", ds: "office_corridor", rt: "08h 19m", st: "CONVERGED", met: "mAP: 0.882" }
                    ]
                    delegate: Rectangle {
                        width: ListView.view.width; height: 36
                        color: index % 2 ? (theme ? theme.backgroundAlt : "#0F172A") : "transparent"
                        Row {
                            anchors.fill: parent; anchors.leftMargin: 16
                            Text { width: 200; anchors.verticalCenter: parent.verticalCenter; text: modelData.job; font.pixelSize: 12; color: theme ? theme.textPrimary : "#E5E7EB" }
                            Text { width: 120; anchors.verticalCenter: parent.verticalCenter; text: modelData.alg; font.pixelSize: 11; color: theme ? theme.textSecondary : "#94A3B8" }
                            Text { width: 120; anchors.verticalCenter: parent.verticalCenter; text: modelData.ds; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            Text { width: 80; anchors.verticalCenter: parent.verticalCenter; text: modelData.rt; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textSecondary : "#94A3B8" }
                            Rectangle {
                                width: 80; height: 18; radius: 9; anchors.verticalCenter: parent.verticalCenter
                                color: modelData.st === "FAILED" ? "#EF444422" : (modelData.st === "STABLE" ? "#10B98122" : "#06B6D422")
                                Text { anchors.centerIn: parent; text: modelData.st; font.pixelSize: 9; font.weight: Font.Bold
                                    color: modelData.st === "FAILED" ? "#EF4444" : (modelData.st === "STABLE" ? "#10B981" : "#06B6D4") }
                            }
                            Item { width: 12; height: 1 }
                            Text { anchors.verticalCenter: parent.verticalCenter; text: modelData.met; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"
                                color: modelData.st === "FAILED" ? "#EF4444" : (theme ? theme.textSecondary : "#94A3B8") }
                        }
                    }
                }
            }
        }
    }
}
