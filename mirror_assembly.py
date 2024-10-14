import os
import NXOpen
import NXOpen.UF
import NXOpen.Features
import NXOpen.Assemblies
import NXOpen.Positioning

def main():
    # session variables
    theSession = NXOpen.Session.GetSession()
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    theUFSession = NXOpen.UF.UFSession.GetUFSession()
    theUI = NXOpen.UI.GetUI()
    lw = theSession.ListingWindow
    lw.Open()
    
    def selectComponents():
        scope = NXOpen.Selection.SelectionScope.AnyInAssembly
        action = NXOpen.SelectionSelectionAction.ClearAndEnableSpecific
        includeFeatures = False
        keepHighlighted = False
        selection = theUI.SelectionManager
        mask = NXOpen.Selection.MaskTriple()
        mask.Type = NXOpen.UF.UFConstants.UF_component_type
        maskArray = [mask]
        components = selection.SelectTaggedObjects("Select components", "Select components to mirror", scope, action, includeFeatures, keepHighlighted, maskArray)
        return components[1]

    def askPlane(title, message, button1, button2):
        message_buttons = NXOpen.UF.Ui.MessageButtons()
        message_buttons.Button1 = True
        message_buttons.Button2 = False
        message_buttons.Button3 = True
        message_buttons.Label1 = button1
        message_buttons.Label2 = None
        message_buttons.Label3 = button2
        message_buttons.Response1 = 1
        message_buttons.Response2 = 0
        message_buttons.Response3 = 2

        resp = theUFSession.Ui.MessageDialog(title, NXOpen.UF.Ui.MessageDialogType.MESSAGE_INFORMATION, message, 1, True, message_buttons)

        if resp == 1:
            return True
        else:
            return False
        
    def askDeleteOriginalObjects(title, message, button1, button2):
        message_buttons = NXOpen.UF.Ui.MessageButtons()
        message_buttons.Button1 = True
        message_buttons.Button2 = False
        message_buttons.Button3 = True
        message_buttons.Label1 = button1
        message_buttons.Label2 = None
        message_buttons.Label3 = button2
        message_buttons.Response1 = 1
        message_buttons.Response2 = 0
        message_buttons.Response3 = 2

        resp = theUFSession.Ui.MessageDialog(title, NXOpen.UF.Ui.MessageDialogType.MESSAGE_INFORMATION, message, 1, True, message_buttons)

        if resp == 1:
            return True
        else:
            return False
        
    def swapGage(name, gage_path):
        name_to_opp_hand = {
            "AS108": "AS109",
            "AS109": "AS108",
            "AS110": "AS111",
            "AS111": "AS110",
            "AS110-CB": "AS111-CB",
            "AS111-CB": "AS110-CB",
            "AS112": "AS113",
            "AS113": "AS112",
            "AS112-CB": "AS113-CB",
            "AS113-CB": "AS112-CB",
            "AS125": "AS129",
            "AS129": "AS125",
            "AS125-CB": "AS129-CB",
            "AS129-CB": "AS125-CB",
            "AS136": "AS137",
            "AS137": "AS136",
            "AS144": "AS145",
            "AS145": "AS144",
            "AS122": "AS130",
            "AS130": "AS122",
            "AS122-CB": "AS130-CB",
            "AS130-CB": "AS122-CB",
            "AS123": "AS124",
            "AS124": "AS123",
            "AS123-CB": "AS124-CB",
            "AS124-CB": "AS123-CB",
            "AS126": "AS127",
            "AS127": "AS126",
            "AS126-CB": "AS127-CB",
            "AS127-CB": "AS126-CB",
            "AS131": "AS132",
            "AS132": "AS131"
        }
        
        opp_hand = name_to_opp_hand[name]
        gage_directory = os.path.join(os.path.dirname(gage_path), opp_hand + ".prt")

        return opp_hand, gage_directory

    def swapShovel(name, shovel_path):
        if "L" in name:
            if "50" in name:
                opp_hand = "GTS-50-50-50-10E-R-200-A"
            else:
                opp_hand = "GTS-75-75-75-10E-R-200-A"
        else:
            if "50" in name:
                opp_hand = "GTS-50-50-50-10E-L-200-A"
            else:
                opp_hand = "GTS-75-75-75-10E-L-200-A"

        shovel_directory = os.path.dirname(shovel_path) + "\\" + opp_hand + ".prt"
        return opp_hand, shovel_directory

    markId1 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")

    components_list = selectComponents()
    if len(components_list) == 0:
        return
    direction = askPlane("Mirror Assembly", ["Select plane to mirror across"], "YZ", "XZ")

    for comp in components_list:
        comp_position = comp.GetPosition()
        basepoint1 = comp_position[0]
        orientation1 = comp_position[1]
        comp_path = comp.Prototype.FullPath
        comp_name = comp.Name
        ref_set = comp.ReferenceSet
        try:
            desc = comp.GetInstanceStringUserAttribute("DESCRIPTION", 0)
        except:
            desc = ""
        new_desc = desc.lower()

        # Component checks for swapping hands/ref sets
        if "gage" in new_desc:
            comp_name, comp_path = swapGage(comp_name, comp_path)
        if "cpi- shovel" in new_desc:
            comp_name, comp_path = swapShovel(comp_name, comp_path)
        if "90 DEG" in ref_set:
            ref_set = "270 DEG"
        elif "270 DEG" in ref_set:
            ref_set = "90 DEG"

        if direction:  # YZ Mirror
            basepoint1.X = -basepoint1.X
            if desc:
                if "CPI-AB-B112-EF-BP" == comp_name or "venturi" in new_desc or "twistlok" in new_desc or "cup holder" in new_desc or "imi- c-clamp" in new_desc or "alum bar" in new_desc or "alum tube" in new_desc or "hs tube" in new_desc or "magnet ball mount" in new_desc or "v120-v144 clamp" in new_desc:
                    orientation1.Xy = -orientation1.Xy  # POS 2
                    orientation1.Xz = -orientation1.Xz
                    orientation1.Yx = -orientation1.Yx
                    orientation1.Zx = -orientation1.Zx
                elif "CPI-AB-750-EF-BP" == comp_name:
                    orientation1.Xx = -orientation1.Xx  # POS 1
                    orientation1.Yx = -orientation1.Yx
                    orientation1.Zy = -orientation1.Zy
                    orientation1.Zz = -orientation1.Zz
                else:
                    orientation1.Xx = -orientation1.Xx  # POS 3
                    orientation1.Yy = -orientation1.Yy
                    orientation1.Yz = -orientation1.Yz
                    orientation1.Zx = -orientation1.Zx
            elif "b112-swivel" == comp_name.lower() or "curve" in comp_name.lower():
                orientation1.Xy = -orientation1.Xy  # POS 2
                orientation1.Xz = -orientation1.Xz
                orientation1.Yx = -orientation1.Yx
                orientation1.Zx = -orientation1.Zx
            elif "temp_brace" in comp_name.lower():
                orientation1.Xx = -orientation1.Xx  # POS 1
                orientation1.Yx = -orientation1.Yx
                orientation1.Zy = -orientation1.Zy
                orientation1.Zz = -orientation1.Zz
            else:
                orientation1.Xx = -orientation1.Xx  # POS 3
                orientation1.Yy = -orientation1.Yy
                orientation1.Yz = -orientation1.Yz
                orientation1.Zx = -orientation1.Zx
        else:  # XZ Mirror
            basepoint1.Y = -basepoint1.Y
            if desc:
                if "CPI-AB-B112-EF-BP" == comp_name or "venturi" in new_desc or "twistlok" in new_desc or "cup holder" in new_desc or "imi- c-clamp" in new_desc or "alum bar" in new_desc or "alum tube" in new_desc or "hs tube" in new_desc or "magnet ball mount" in new_desc or "v120-v144 clamp" in new_desc:
                    orientation1.Xx = -orientation1.Xx  # POS 2
                    orientation1.Xz = -orientation1.Xz
                    orientation1.Yy = -orientation1.Yy
                    orientation1.Zy = -orientation1.Zy
                elif "CPI-AB-750-EF-BP" == comp_name:
                    orientation1.Xy = -orientation1.Xy  # POS 1
                    orientation1.Yy = -orientation1.Yy
                    orientation1.Zx = -orientation1.Zx
                    orientation1.Zz = -orientation1.Zz
                else:
                    orientation1.Xy = -orientation1.Xy  # POS 3
                    orientation1.Yx = -orientation1.Yx
                    orientation1.Yz = -orientation1.Yz
                    orientation1.Zy = -orientation1.Zy
            elif "b112-swivel" == comp_name.lower() or "curve" in comp_name.lower():
                orientation1.Xx = -orientation1.Xx  # POS 2
                orientation1.Xz = -orientation1.Xz
                orientation1.Yy = -orientation1.Yy
                orientation1.Zy = -orientation1.Zy
            elif "temp_brace" in comp_name.lower():
                orientation1.Xy = -orientation1.Xy  # POS 1
                orientation1.Yy = -orientation1.Yy
                orientation1.Zx = -orientation1.Zx
                orientation1.Zz = -orientation1.Zz
            else:
                orientation1.Xy = -orientation1.Xy  # POS 3
                orientation1.Yx = -orientation1.Yx
                orientation1.Yz = -orientation1.Yz
                orientation1.Zy = -orientation1.Zy

        addcomp1 = workPart.ComponentAssembly.AddComponent(comp_path, ref_set, comp_name, basepoint1, orientation1, -1, True)
        theSession.UpdateManager.AddToDeleteList(comp)

    if askDeleteOriginalObjects("Component Deletion", ["Delete original components?"], "No", "Yes"):
        theSession.UpdateManager.ClearDeleteList()
    else:
        markId2 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Delete comps")
        theSession.UpdateManager.DoUpdate(markId1)

    lw.Close()

if __name__ == "__main__":
    main()

