 using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;

public class GUI_Stuff : MonoBehaviour
{
	private Rect windowRect = new Rect (100, 100, 500, 500);

	public List<string> fullSectionList;					//List of all sections
	public List<string> tfactorList;
	public List<string> selectedFactorList;

	private List<bool> factorToggle = new List<bool>();		//Says which transcription factors are on/off

	bool editing = false;
	string selectedItem = "";

	int offset = 100;


	//Direct buffer to the screen
	public simParams GUIParams;

	public GUIStyle header;
	public GUIStyle tinyText;

	public GUISkin test;

	bool showButton;
	bool paramsOn;


	public Vector2 scrollPosition1 = Vector2.zero;
	public Vector2 scrollPosition2 = Vector2.zero;

	public float vSbarValue;


	//"ACTIVE" FUNCIONS--------------------------------------------
	//Called once for initialization
	void Start()
	{
		GUIParams = new simParams ();
		fullSectionList = GUIParams.initialize_defaults ();
		fullSectionList = GUIParams.read ("SAMPLE_TRAPP.ini");

		showButton = true;
		paramsOn = false;

		string[] tlist = {"REB1", "MCM1", "RSC3", "TEC1", "STE12", "FLO8", "SFL1", "GAL4"}; 
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
		GUI.skin = test;


		if (GUI.Button (new Rect (10, 10, 150, 50), "PARAMETERS"))
		{ 
			if (paramsOn)
					paramsOn = false;
			if (!paramsOn)
					paramsOn = true;
		}

		if (paramsOn)
		{
			windowRect = GUI.Window (0, windowRect, WindowFunction, "My Window");
		}

		//Debug.Log (paramsOn);
		
		
		          

	
	}



	
	//"INACTIVE" FUNCIONS--------------------------------------------
	void WindowFunction (int WindowID)
	{

		//Rect sectionRect = new Rect (10, 20, 70, 20);
		Rect tfactorRect = new Rect (250, 20, 70, 20);


		//Display 'TRAPP', 'NUCLEOSOME', 'RNAP' sections
		DisplaySection ("TRAPP", new Rect (15, 20, 70, 20), true);
		DisplaySection ("NUCLEOSOME", new Rect (15, 200, 70, 20), true);
		DisplaySection ("RNAP", new Rect (15, 300, 70, 20), true);


		//Scrollable list of checkboxes
		selectedFactorList = ComboBoxToggleList (tfactorRect, tfactorList);


		//Display editable transcription factor dropdown
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





	