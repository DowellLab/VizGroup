using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;

/* string ComboBoxList(Rect r, List<string> s)
 * r - rectangle object used to designate position & dimensions in screen space
 * s - list of string objects that will act as the drop down list.
 * Return Value - Returns the string object selected by user
 * 
 * Function - Creates a dropdown menu with a number of options designated by the user, 
 * also known as a combobox. If the number of items in the menu exceeds the height of the rectangle,
 * a scrollbar pops up and the user can scroll through the items.
 * 
 */

/* string ComboBox(Rect r, List<string> s)
 * 
 * Function - Same as ComboBoxList but without the scrollbar
 * 
 */

/* List<string> ComboToggleList(Rect r, List<string> s)
 * 'r' - rectangle object used to designate position & dimensions in screen space.
 * 's' - list of string objects that will act as the drop down toggle list.
 * Return Value - Returns a list of the string objects selected by user
 * 
 * Function - Creates a dropdown toggle menu with a number of options designated by the user, 
 * also known as a combobox. If the number of items in the menu exceeds the height of the rectangle,
 * a scrollbar pops up and the user can scroll through the items.
 * 
 */


/* void DisplaySection(string sectionLabel, Rect sectionRect, bool DisplayLabel)
 * 'sectionLabel' - section from simParams object whose attributes we wish to display.
 * 'sectionRect' - rectangle object used to designate position & dimensions in screen space.
 * 'DisplayLabel' - flag indicating whether to display the actual section name or not.
 * Return Value - none
 * 
 * Function - This function is very specific to the app and simParams class. It takes a 
 * section (sectionLabel) from the Params structure and displays all of that section's 
 * attributes with fields to change the attributes.
 */



public class GUI_Stuff : MonoBehaviour
{
	private Rect windowRect = new Rect (100, 100, 500, 500);

	//List of all sections
	public List<string> fullSectionList;	

	public List<string> tfactorList;
	public List<string> selectedFactorList;

	//Says which transcription factors are on/off
	private List<bool> factorToggle = new List<bool>();		

	bool editing = false;
	string selectedItem = "";
	
	//simParams object holding all parameters for current session.
	public simParams GUIParams;
	
	public GUIStyle tinyText;
	public GUISkin test;

	//Indicating whether to show parameters window or not
	bool paramsOn;

	//Variables for the scrolling GUI elements
	public Vector2 scrollPosition1 = Vector2.zero;
	public Vector2 scrollPosition2 = Vector2.zero;
	public float vSbarValue;

	
	//Called once for initialization
	void Start()
	{
		GUIParams = new simParams ();
		fullSectionList = GUIParams.initialize_defaults ();
		fullSectionList = GUIParams.read ("SAMPLE_TRAPP.ini");

		paramsOn = false;

		string[] tlist = {"REB1", "MCM1", "RSC3", "TEC1", "STE12", "FLO8", "SFL1", "GAL4"}; 
		//An attempt at an exhaustive list of all transcription factors that could be possible
		string[] alltlist = {
			"REB1",
			"MCM1",
			"RSC3",
			"TEC1",
			"STE12",
			"FLO8",
			"SFL1",
			"GAL4",
			"DAL80",
			"GAL4",
			"GTS1",
			"HAP3",
			"NRG1",
			"PHO2",
			"PHO4",
			"RAP1",
			"RIM101",
			"SOK2",
			"STE13",
			"TBP",
			"YAP5"
		}; 
		tfactorList = new List<string> (tlist);
		selectedFactorList = new List<string> ();
		for (int i = 0; i < tfactorList.Count; ++i)
		{
			factorToggle.Add (false);
		}


	}

	//Called every frame
	void OnGUI ()
	{
		//Setup skin for User Interface
		GUI.skin = test;

		//Button to open the GUI window
		if (GUI.Button (new Rect (10, 10, 150, 50), "PARAMETERS"))
		{ 
			if (paramsOn)
				paramsOn = false;
			else
				paramsOn = true;
			
		}

		//Open GUI window
		if (paramsOn)
		{
			windowRect = GUI.Window (0, windowRect, WindowFunction, "My Window");
		}
	}



	// Creates the window encapsulating the GUI elements
	void WindowFunction (int WindowID)
	{

		Rect tfactorRect = new Rect (250, 20, 70, 20);


		//Display 'TRAPP', 'NUCLEOSOME', 'RNAP' panel sections
		DisplaySection ("TRAPP", new Rect (15, 20, 70, 20), true);
		DisplaySection ("NUCLEOSOME", new Rect (15, 200, 70, 20), true);
		DisplaySection ("RNAP", new Rect (15, 300, 70, 20), true);


		//Scrollable list of Transcription Factor checkboxes
		selectedFactorList = ComboBoxToggleList (tfactorRect, tfactorList);


		//Display editable Transcription Factor dropdown
		string item = ComboBoxButtonList (new Rect(320, 200, 60, 20), selectedFactorList);

		//If factor is selected to edit
		if(item != "") 
		{
			//If key is not in dictionary, add it
			if(!GUIParams.dict.ContainsKey(item))
				AddTFAttributes(ref GUIParams, item);

			//Display editable TF
			DisplaySection(item, new Rect(325, 225, 50, 20), false);
		}

		//Writes out the user defined settings to new .ini file.
		if(GUI.Button (new Rect(275, 375, 150, 50), "SUBMIT"))
			GUIParams.write ("GUIParamsTest.ini");

			//Make this window draggable
			GUI.DragWindow ();
	}
	

	string ComboBox(Rect r, List<string> s)
	{
		//Click dropdown
		if (GUI.Button (r, selectedItem)) 
		{
			editing = true;
		}

		//We are looking at dropdown menu
		if(editing)
		{
			for(int i = 0; i < s.Count; ++i)
			{
				if(GUI.Button(new Rect(r.x, r.y+r.height + r.height*i, r.width, r.height), s[i]))
				{
					selectedItem = s[i];
					editing = false;
				}
			}
			if(editing)
				selectedItem = "";

		}
		return selectedItem;
	}


	string ComboBoxButtonList(Rect r, List<string> s)
	{
		bool scrollOn;
		if (s.Count * r.height > 100)
			scrollOn = true;
		else 
			scrollOn = false;
	
		//GUI.Label (new Rect(r.x, r.y, 300, 20), "Transcription Factors", tinyText);
		if (GUI.Button (r, selectedItem)) 
			editing = true;


		//Looking at dropdown menu
		if (editing) 
		{
			//Select with scrollview on
			if(scrollOn)
			{
				scrollPosition1 = GUI.BeginScrollView (new Rect (r.x, r.y, 100, 100), scrollPosition1, new Rect (0, 0, 80, 500));
				for (int i = 0; i < s.Count; ++i) 
				{
						//If we select from drop down menu
						if (GUI.Button (new Rect (0, 0 + r.height + r.height * i, r.width, r.height), s [i]))
						{
							selectedItem = s [i];
							editing = false;
						}

				}
			}
			//Select with scrollview off
			else
			{
				for (int i = 0; i < s.Count; ++i) 
				{
					//If we select from drop down menu
					if (GUI.Button (new Rect (r.x, r.y + r.height + r.height * i, r.width, r.height), s [i]))
					{
						selectedItem = s [i];
						editing = false;
					}
				}
			}

			//If we didn't select anything from dropdown
			if (editing)
			{
				selectedItem = "";
			}

			if(scrollOn)
				GUI.EndScrollView ();
		}

		return selectedItem;
	}


	List<string> ComboBoxToggleList(Rect r, List<string> inputList)
	{
		List<string> selectedList = new List<string> ();
		//Display Transcription Factor checkboxes
		GUI.Label (new Rect(r.x, r.y, 200, 20), "TRANSCRIPTION FACTORS");
		
		r.y += 30;
		scrollPosition2 = GUI.BeginScrollView (new Rect (r.x + r.width, r.y, 100, 100), scrollPosition2, new Rect (0, 0, 50, 500));
		r.y -= 30;
		for (int i = 0; i < inputList.Count; ++i) 
		{
			factorToggle[i] = ( GUI.Toggle (new Rect(0, i*20, 70, 20), factorToggle[i], inputList[i]) );
			r.y += 20;
			if(factorToggle[i])
			{
				if(!selectedFactorList.Contains(inputList[i]))
					selectedFactorList.Add(inputList[i]);
			}
			else
			{
				if(selectedFactorList.Contains(inputList[i]))
					selectedFactorList.Remove(inputList[i]);
			}
		}
		GUI.EndScrollView ();

		return selectedFactorList;
	}

	
	void DisplaySection(string sectionLabel, Rect sectionRect, bool DisplayLabel)
	{
		if (DisplayLabel) 
		{
			GUI.Label (new Rect (sectionRect.x, sectionRect.y, 150, 20), sectionLabel);
			sectionRect.y += 20;
		}

		//Showing attribute/value pairs
		foreach (KeyValuePair<string, string> attr in GUIParams.dict[sectionLabel])
		{
			string s = CompoundControls.LabelTextField (sectionRect, attr.Key, attr.Value, tinyText);
			GUIParams.add_string(sectionLabel, attr.Key, s);
			sectionRect.y += 20;
		}
	}


	void AddTFAttributes(ref simParams s, string sectionLabel)
	{	
		s.add_string(sectionLabel, "INITIAL_COUNT", "");
		s.add_string(sectionLabel, "ON_RATE", "");
		s.add_string(sectionLabel, "MOTIF_THRESH", "");
	}
	




}





	