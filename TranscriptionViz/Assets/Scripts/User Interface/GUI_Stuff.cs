 using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;

public class GUI_Stuff : MonoBehaviour
{
	private Rect windowRect = new Rect (100, 100, 500, 500);

//	private Rect scrollRect = new Rect (100, 100, 500, 500);

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


	//Scrolling variables
	bool scrollOn;


	public Vector2 scrollPosition = Vector2.zero;

	public float vSbarValue;


	//"ACTIVE" FUNCIONS--------------------------------------------
	//Called once for initialization
	void Start()
	{
		GUIParams = new simParams ();
		fullSectionList = GUIParams.initialize_defaults ();
		fullSectionList = GUIParams.read ("SAMPLE_TRAPP.ini");

		showButton = true;
		scrollOn = true;

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

			//vSbarValue = GUI.VerticalScrollbar(new Rect(Screen.width, Screen.height, 100, 30), vSbarValue, 1.0F, 10.0F, 0.0F);

			
//			scrollPosition = GUI.BeginScrollView(new Rect(Screen.width/2, Screen.height/2, 50, 100), scrollPosition, new Rect(0, 0, 50, 200));
//			GUI.Button(new Rect(0, 0, 100, 20), "Top-left");
//			GUI.Button(new Rect(120, 0, 100, 20), "Top-right");
//			GUI.Button(new Rect(0, 180, 100, 20), "Bottom-left");
//			GUI.Button(new Rect(120, 180, 100, 20), "Bottom-right");
//			GUI.EndScrollView();


			

		 windowRect = GUI.Window(0, windowRect, WindowFunction, "My Window");
		          

//		if(GUI.Button (new Rect(100, Screen.height / 2, 150, 50), "WRITE TO FILE"))
//			GUIParams.write ("GUIParamsTest.ini");
	}



	
	//"INACTIVE" FUNCIONS--------------------------------------------
	void WindowFunction (int WindowID)
	{

//		Rect sectionRect = new Rect (10, 20, 70, 20);
		Rect tfactorRect = new Rect (250, 20, 70, 20);


		//Display 'TRAPP', 'NUCLEOSOME', 'RNAP' sections

		DisplaySection ("TRAPP", new Rect (15, 20, 70, 20));
		DisplaySection ("NUCLEOSOME", new Rect (15, 200, 70, 20));
		DisplaySection ("RNAP", new Rect (15, 300, 70, 20));



		//Display Transcription Factor checkboxes
		GUI.Label (new Rect(tfactorRect.x, tfactorRect.y, 200, 20), "TRANSCRIPTION FACTORS");

		tfactorRect.y += 30;
		scrollPosition = GUI.BeginScrollView (new Rect (tfactorRect.x + tfactorRect.width, tfactorRect.y, 100, 200), scrollPosition, new Rect (0, 0, 50, 1000));
		tfactorRect.y -= 30;
		for (int i = 0; i < tfactorList.Count; ++i) 
		{
			factorToggle[i] = ( GUI.Toggle (new Rect(0, i*20, 70, 20), factorToggle[i], tfactorList[i]) );
			tfactorRect.y += 20;
			if(factorToggle[i])
			{
				if(!selectedFactorList.Contains(tfactorList[i]))
					selectedFactorList.Add(tfactorList[i]);
			}
			else
			{
				if(selectedFactorList.Contains(tfactorList[i]))
					selectedFactorList.Remove(tfactorList[i]);
			}
		}
		GUI.EndScrollView ();

		//Display editable transcription factor dropdown
		//string item = ComboBox (new Rect(tfactorRect.x, tfactorRect.y += offset, 60, 20), selectedFactorList);

		string item = ComboBoxList (new Rect(tfactorRect.x, tfactorRect.y += offset, 60, 20), selectedFactorList);
		//If factor is selected to edit
		if(item != "") 
		{
			if(!GUIParams.dict.ContainsKey(item))
			{
				AddTFAttributes(ref GUIParams, item);
	    	}

			//GUI.Label (new Rect (tfactorRect.x, tfactorRect.y += offset, tfactorRect.width, tfactorRect.height), item);
			tfactorRect.y += 30;
			foreach (KeyValuePair<string, string> attr in GUIParams.dict[item])
			{
				string s = CompoundControls.LabelTextField (tfactorRect, attr.Key, attr.Value, test.label);
				GUIParams.add_string (item, attr.Key, s);
				tfactorRect.y += 20;
			}
		}







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


	string ComboBoxList(Rect r, List<string> s)
	{
		if (s.Count * r.height > 200)
			scrollOn = true;
		else 
			scrollOn = false;
	
		//GUI.Label (new Rect(r.x, r.y, 300, 20), "Transcription Factors", tinyText);
		if (GUI.Button (r, selectedItem)) 
		{
			editing = true;
		}

		//Looking at dropdown menu
		if (editing) 
		{
			//Begin scrollview
			if(scrollOn)
			{
				scrollPosition = GUI.BeginScrollView (new Rect (r.x, r.y, 100, 200), scrollPosition, new Rect (0, 0, 80, 7000));
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



	void DisplaySection(string sectionLabel, Rect sectionRect)
	{
		GUI.Label (new Rect(sectionRect.x, sectionRect.y, 100.0f, 20.0f), sectionLabel);
		sectionRect.y += 20;

		//Showing attribute/value pairs
		foreach (KeyValuePair<string, string> attr in GUIParams.dict[sectionLabel])
		{
			string s = CompoundControls.LabelTextField (sectionRect, attr.Key, attr.Value, test.label);
			GUIParams.add_string(sectionLabel, attr.Key, s);
			sectionRect.y += 20;
		}
		sectionRect.y += 50;
	}


	void AddTFAttributes(ref simParams s, string sectionLabel)
	{	
		s.add_string(sectionLabel, "INITIAL_COUNT", "");
		s.add_string(sectionLabel, "ON_RATE", "");
		s.add_string(sectionLabel, "MOTIF_THRESH", "");
	}
	




}





	