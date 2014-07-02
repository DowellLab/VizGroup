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

	public int FrameCount = 1;
//	public int iterations = 0;

	//Play/Pause Button
	private Rect rect = new Rect(0, Screen.height - 100, 100, 100);
	public bool started = false;
	public static bool finished = false;

	// Use this for initialization
	void Start () {
	
		StartCoroutine_Auto (TimeStep.instance.InitialTimestep ());


	}

	// Update is called once per frame
	void Update () 
	{
		if (Input.GetMouseButtonDown(0)) {
			if(rect.Contains (new Vector2(Input.mousePosition.x, Screen.height - Input.mousePosition.y))) {
				Debug.Log(Input.mousePosition);
				//simulation has not started
				if(!started || finished){
					StartCoroutine_Auto (TimeStep.instance.ReadFile ());
					started = true;
					finished = false;
				}
				//simulation has already started
				else if (started && TimeStep.instance.isPaused == false) {
					TimeStep.instance.PauseTimeStep ();
				}
				else if (started && TimeStep.instance.isPaused == true) {
					TimeStep.instance.UnpauseTimeStep ();
				}
			}
			
		}
	}

	void OnGUI()
	{
		//Display play button if paused
		if (TimeStep.instance.isPaused == false && started == false || finished) {
			GUI.DrawTexture (rect, Resources.Load<Texture2D> ("Play_button"));
		} 
		else if (TimeStep.instance.isPaused == false && started == true) {
			GUI.DrawTexture (rect, Resources.Load<Texture2D> ("Pause_button"));	
		}
		else if (TimeStep.instance.isPaused == true && started == true) {
			GUI.DrawTexture (rect, Resources.Load<Texture2D> ("Play_button"));	
		}
		else if (finished) {
			GUI.DrawTexture (rect, Resources.Load<Texture2D> ("Play_button"));
		}


		// Increases by ? every second
			FrameCount++;

//			Debug.Log (FrameCount);

		}
		
	}
//}
