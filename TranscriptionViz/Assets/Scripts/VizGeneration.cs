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

	public static int startStep = 500;

	public int FrameCount = 1;
//	public int iterations = 0;

	//Play/Pause Button
	private Rect rect = new Rect(0, Screen.height - 100, 100, 100);
	public bool started = false;
	public static bool finished = false;

	// FastForward Button
	private Rect ffRect = new Rect(100, Screen.height - 100, 100, 100);

	// Slow Button
	private Rect slowRect = new Rect(200, Screen.height - 100, 100, 100);

	// Display Time.Timescale
//	public static float currentTimescale = Time.timeScale;

	public static bool splashed = false;


	// Use this for initialization
	void Start () {
		if(!splashed)
		{
			Application.LoadLevel("Splash");
			splashed = true;
		}
		StartCoroutine_Auto (TimeStep.instance.InitialTimestep ());


	}

	// Update is called once per frame
	void Update () 
	{
		if (Input.GetMouseButtonDown(0)) {
			// Play And Pause
			if(rect.Contains (new Vector2(Input.mousePosition.x, Screen.height - Input.mousePosition.y))) {
//				Debug.Log(Input.mousePosition);
				//simulation has not started
				if(!started || finished){
					TimeStep.DestroyObjects ();
					StartCoroutine_Auto (TimeStep.instance.ReadFile (startStep));
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

			// Fastforward
			if (ffRect.Contains(new Vector2(Input.mousePosition.x, Screen.height - Input.mousePosition.y)))
			{
				if (started == true)
				{
					if (Time.timeScale < 64)
					{
						Time.timeScale *= 2;

					}
				}
			}

			// Slow
			if (slowRect.Contains(new Vector2(Input.mousePosition.x, Screen.height - Input.mousePosition.y)))
			{
				if (started == true)
				{
					if (Time.timeScale >= 0.5f)
					{
						Time.timeScale = Time.timeScale / 2;

					}
				}
			}


			
		}
	}

	void OnGUI()
	{
		// Display play button if paused
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

		// Always display fastforward button and slow button
		GUI.DrawTexture (ffRect, Resources.Load<Texture2D> ("fastForward_button"));
		GUI.DrawTexture (slowRect, Resources.Load<Texture2D> ("slow_button"));

		// Displays current TimeScale
		GUI.Label (new Rect (175, Screen.height - 120, 100, 20), "Time X" + Time.timeScale.ToString());
		
		//Exit Button
		if (GUI.Button (new Rect (Screen.width - 80 , 0, 80, 20), "EXIT")) {
			Application.Quit();
		}

			
		// Increases by ? every second
			FrameCount++;

//			Debug.Log (FrameCount);

		}
		
	}
//}
