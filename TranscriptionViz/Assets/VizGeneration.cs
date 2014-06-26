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


//public static class StreamExtensions
//{
//	public static void CopyTo(this Stream input, Stream output)
//	{
//		if (input == null)
//		{
//			throw new ArgumentNullException("input");
//		}
//		if (output == null)
//		{
//			throw new ArgumentNullException("output");
//		}
//						
//		byte[] buffer = new byte[8192];
//		int bytesRead;
//
//		while ((bytesRead = input.Read(buffer, 0, buffer.Length)) > 0)
//		{
//			output.Write(buffer, 0, bytesRead);
//		}
//	}
//}




public class VizGeneration : MonoBehaviour {

	public int j = 0;
	public int FrameCount = 1;
//	public int iterations = 0;


	// Use this for initialization
	void Start () {
	
		TimeStep.InitialTimestep ();


	}

	// Update is called once per frame
	void Update () 
	{
//		OnGUI ();

	}

	void OnGUI()
	{
	
		// Starts at 2nd timestep currently	
		if (GUI.Button (new Rect (10, 10, 50, 50), "Start")) {
		
			StartCoroutine_Auto (TimeStep.instance.ReadFile ());
				
		}
				
			


		// Increases by ? every second
			FrameCount++;

//			Debug.Log (FrameCount);

		}
		
	}
//}
