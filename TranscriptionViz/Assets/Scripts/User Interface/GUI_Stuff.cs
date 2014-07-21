using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;

public class GUI_Stuff : MonoBehaviour
{
	private Rect windowRect = new Rect (100, 100, 500, 500);
	public List<string> dummyValue;
	public string dummyValueX;
	public string dummyValueY;
	public string dummyValueZ;

	private float hScrollbarValue;

	//Used to be what is displayed directly
	public simParams GUIParams;

	void Start()
	{
		GUIParams = new simParams ();
		GUIParams.initialize_defaults ();
		Debug.Log ("Here!");
	}

	void OnGUI ()
	{
		windowRect = GUI.Window(0, windowRect, WindowFunction, "My Window");
	}

	void WindowFunction (int WindowID)
	{
		toolBar(new Rect (10, 20, 200, 30));
		GUI.DragWindow ();
		// Draw any controls inside the window here
	}

	void toolBar (Rect screenRect)
	{
		screenRect.x += 10;
		screenRect.y += 10;

		foreach (KeyValuePair<string, Dictionary<string, object>> sec in GUIParams.dict)
			screenRect.y = DisplaySection (sec.Key, screenRect.x, screenRect.y);

	}



	float DisplaySection(string sectionLabel, float x, float y)
	{
		GUI.Label (new Rect(x, y, 100.0f, 20.0f), sectionLabel);
		Rect attrRect = new Rect (x, y + 20.0f, 70.0f, 20.0f);

		foreach (KeyValuePair<string, object> attr in GUIParams.dict[sectionLabel])
		{
			dummyValue.Add(CompoundControls.LabelTextField (attrRect, attr.Key, attr.Value.ToString()));
			attrRect.y += 20;
		}

		return attrRect.y;
	}


}





	