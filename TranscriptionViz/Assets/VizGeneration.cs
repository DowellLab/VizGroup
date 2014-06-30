using UnityEngine;
using System.Collections;
using System.Xml.Linq;
using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.Reflection;
using System.Linq;
using System.Xml;

public class VizGeneration : MonoBehaviour {

//	public int j = 0;
	public int FrameCount = 1;
//	public int iterations = 0;


	// Use this for initialization
	void Start () {
	
		StartCoroutine_Auto (TimeStep.instance.InitialTimestep ());


	}

	// Update is called once per frame
	void Update () 
	{

	}

	void OnGUI()
	{

		/* Chad's non-working code
		Rect rect = new Rect(0, Screen.height - 60, 60, 60);
		GUI.DrawTexture(rect, Resources.Load("Play_button"));
		Event e = Event.current.mousePosition;
		if (rect.Contains (e)) {
			Debug.Log("HEEEEEEEEEEEY!");

		}
		*/
	
		// Starts at 2nd timestep currently	
		if (GUI.Button (new Rect (10, 10, 50, 50), "Start")) 
		{
		
			StartCoroutine_Auto (TimeStep.instance.ReadFile ());
				
		}


		if (GUI.Button (new Rect (75, 10, 50, 50), "Pause")) 
		{
			if (TimeStep.instance.isPaused == false)
			{
				TimeStep.instance.PauseTimeStep ();

			} else {
				TimeStep.instance.UnpauseTimeStep ();
			}


		}


		// Increases by ? every second
			FrameCount++;

//			Debug.Log (FrameCount);

		}
		
	}
//}
