// Copyright (c) 2016 Ultimaker B.V.
// 
// proterties values
//   "SSize"    : Tab Size in mm
//   "SOffset"  : Offset set on Tab in mm
//   "SCapsule" : Define as capsule
//   "NLayer"   : Number of layer
//

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.1 as UM

Item
{
    id: base
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name: "cura"}


    Grid
    {
        id: textfields

        anchors.leftMargin: UM.Theme.getSize("default_margin").width
        anchors.top: parent.top

        columns: 2
        flow: Grid.TopToBottom
        spacing: Math.round(UM.Theme.getSize("default_margin").width / 2)

        Label
        {
            height: UM.Theme.getSize("setting_control").height
            text: "Size"
            font: UM.Theme.getFont("default")
            color: UM.Theme.getColor("text")
            verticalAlignment: Text.AlignVCenter
            renderType: Text.NativeRendering
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }

        Label
        {
            height: UM.Theme.getSize("setting_control").height
            text: "X/Y Distance"
            font: UM.Theme.getFont("default")
            color: UM.Theme.getColor("text")
            verticalAlignment: Text.AlignVCenter
            renderType: Text.NativeRendering
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }

        Label
        {
            height: UM.Theme.getSize("setting_control").height
            text: "Number of layers"
            font: UM.Theme.getFont("default")
            color: UM.Theme.getColor("text")
            verticalAlignment: Text.AlignVCenter
            renderType: Text.NativeRendering
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }
		
		TextField
        {
            id: sizeTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            property string unit: "mm"
            style: UM.Theme.styles.text_field
            text: UM.ActiveTool.properties.getValue("SSize")
            validator: DoubleValidator
            {
                decimals: 2
                bottom: 0.1
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("SSize", modified_text)
            }
        }
		TextField
        {
            id: offsetTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            property string unit: "mm"
            style: UM.Theme.styles.text_field
            text: UM.ActiveTool.properties.getValue("SOffset")
            validator: DoubleValidator
            {
                decimals: 3
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("SOffset", modified_text)
            }
        }

		TextField
        {
            id: numberlayerTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            style: UM.Theme.styles.text_field
            text: UM.ActiveTool.properties.getValue("NLayer")
            validator: IntValidator
            {
				bottom: 1
				top: 10
            }

            onEditingFinished:
            {
                UM.ActiveTool.setProperty("NLayer", text)
            }
        }		
    }
	
	CheckBox
	{
		id: useCapsuleCheckbox
		anchors.top: textfields.bottom
		anchors.topMargin: UM.Theme.getSize("default_margin").height
		anchors.left: parent.left
		text: catalog.i18nc("@option:check","Define as Capsule")
		style: UM.Theme.styles.partially_checkbox
		checked: UM.ActiveTool.properties.getValue("SCapsule")
		onClicked: UM.ActiveTool.setProperty("SCapsule", checked)
	}
	
	Rectangle {
        id: topRect
        anchors.top: useCapsuleCheckbox.bottom 
		color: "#00000000"
		width: UM.Theme.getSize("setting_control").width * 1.3
		height: UM.Theme.getSize("setting_control").height 
        anchors.left: parent.left
		anchors.topMargin: UM.Theme.getSize("default_margin").height
    }
	
	Button
	{
		id: removeAllButton
		anchors.centerIn: topRect
		spacing: UM.Theme.getSize("default_margin").height
		width: UM.Theme.getSize("setting_control").width
		height: UM.Theme.getSize("setting_control").height
		highlighted : true		
		text: catalog.i18nc("@label", UM.ActiveTool.properties.getValue("SMsg"))
		onClicked: UM.ActiveTool.triggerAction("removeAllSupportMesh")
	}
	
	Rectangle {
        id: bottomRect
        anchors.top: topRect.bottom
		//color: UM.Theme.getColor("toolbar_background")
		color: "#00000000"
		width: UM.Theme.getSize("setting_control").width * 1.3
		height: UM.Theme.getSize("setting_control").height 
        anchors.left: parent.left
		anchors.topMargin: UM.Theme.getSize("default_margin").height
    }
	
	Button
	{
		id: addAllButton
		anchors.centerIn: bottomRect
		spacing: UM.Theme.getSize("default_margin").height
		width: UM.Theme.getSize("setting_control").width
		height: UM.Theme.getSize("setting_control").height
		highlighted : true		
		text: catalog.i18nc("@label", "Automatic Addition")
		onClicked: UM.ActiveTool.triggerAction("addAutoSupportMesh")
	}
	

	CheckBox
	{
		id: useAreaCheckbox
		anchors.top: bottomRect.bottom
		text: catalog.i18nc("@option:check","Set On Adhesion Area")
		style: UM.Theme.styles.partially_checkbox
		checked: UM.ActiveTool.properties.getValue("SArea")
		onClicked: UM.ActiveTool.setProperty("SArea", checked)
	}
}
