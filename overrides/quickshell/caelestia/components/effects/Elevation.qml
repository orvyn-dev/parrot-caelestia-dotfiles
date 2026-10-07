// Qt 6.8 compatibility replacement, prepared 2026-10-07.
// Derived from Caelestia v1.1.1; distributed under GNU GPL version 3.
import ".."
import qs.services
import QtQuick
import QtQuick.Effects

Item {
    id: root

    property int level
    property real dp: [0, 1, 3, 6, 8, 12][level]
    property real radius: 0
    property color color: Qt.alpha(Colours.palette.m3shadow, 0.7)
    property real blur: (dp * 5) ** 0.7
    property real spread: -dp * 0.3 + (dp * 0.1) ** 2
    property vector2d offset: Qt.vector2d(0, dp / 2)

    Behavior on dp {
        Anim {}
    }

    Rectangle {
        id: shadowShape

        x: -root.spread + root.offset.x
        y: -root.spread + root.offset.y
        width: Math.max(0, root.width + 2 * root.spread)
        height: Math.max(0, root.height + 2 * root.spread)
        radius: Math.max(0, root.radius + root.spread)
        color: root.color
        antialiasing: true
        visible: false
        layer.enabled: true
    }

    MultiEffect {
        anchors.fill: shadowShape
        source: shadowShape
        blurEnabled: true
        blurMax: 24
        blur: Math.max(0, Math.min(1, root.blur / blurMax))
        autoPaddingEnabled: true
    }
}
