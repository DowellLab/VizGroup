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

public class VizGeneration : MonoBehaviour {

	// Use this for initialization
	void Start () {
	
		TimeStep.InitialTimestep();

	}

	// Update is called once per frame
	void Update () 
	{
//		if (Input.GetKeyDown("space"))
//		{
//			TimeStep.ReadFile ();
//		}
	}

	void OnGUI()
	{
		if (GUI.Button(new Rect(10, 10, 50, 50), "Start"))
		{
			TimeStep.ReadFile ();
		}

	}



}