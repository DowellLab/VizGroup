using UnityEngine;
// Popup list created by Eric Haines
// ComboBox Extended by Hyungseok Seo.(Jerry) sdragoon@nate.com
// 
// -----------------------------------------------
// This code working like ComboBox Control.
// I just changed some part of code, 
// because I want to seperate ComboBox button and List.
// ( You can see the result of this code from Description's last picture )
// -----------------------------------------------
//
// === usage ======================================
//
 public class SomeClass : MonoBehaviour
 {
	GUIContent[] comboBoxList;
	private ComboBox comboBoxControl = new ComboBox();
	private GUIStyle listStyle = new GUIStyle();

	private void Start()
	{
	    comboBoxList = new GUIContent[5];
	    comboBoxList[0] = new GUIContent("Thing 1");
	    comboBoxList[1] = new GUIContent("Thing 2");
	    comboBoxList[2] = new GUIContent("Thing 3");
	    comboBoxList[3] = new GUIContent("Thing 4");
	    comboBoxList[4] = new GUIContent("Thing 5");

	    listStyle.normal.textColor = Color.white; 
	    listStyle.onHover.background =
	    listStyle.hover.background = new Texture2D(2, 2);
	    listStyle.padding.left =
	    listStyle.padding.right =
	    listStyle.padding.top =
	    listStyle.padding.bottom = 4;
	}

	private void OnGUI () 
	{
	    int selectedItemIndex = comboBoxControl.GetSelectedItemIndex();
	    selectedItemIndex = comboBoxControl.List( 
			new Rect(50, 100, 100, 20), comboBoxList[selectedItemIndex].text, comboBoxList, listStyle );
          GUI.Label( new Rect(50, 70, 400, 21), 
			"You picked " + comboBoxList[selectedItemIndex].text + "!" );
	}
 }

// =================================================