using UnityEngine;
using System.Collections;
using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.Reflection;
using System.Linq;



public class TimeStep : MonoBehaviour
{

	//Implement Destruction of Objects
	static public void DestroyObjects()
	{
		GameObject[] nucleosomes = GameObject.FindGameObjectsWithTag ("Nucleosome");
		GameObject[] transcriptionFactors = GameObject.FindGameObjectsWithTag("TranscriptionFactor");
		GameObject[] transcriptionalMachineries = GameObject.FindGameObjectsWithTag("TranscriptionalMachinery");

		foreach (GameObject go in nucleosomes)
		{
			Destroy (go);
		}

		foreach (GameObject go in transcriptionFactors)
		{
			Destroy (go);
		}

		foreach (GameObject go in transcriptionalMachineries)
		{
			Destroy (go);
		}
			
	}


	// Implement waiting
	static public TimeStep instance;

	static public bool readyForNext = true;

	void Awake()
	{
		instance = this;
		Application.targetFrameRate = 300;
	}

	static public void DoCoroutine()
	{
		instance.StartCoroutine ("JustWait");
	}
		

	IEnumerator JustWait()
	{
		readyForNext = false;
		Debug.Log("Start waiting.");
		yield return new WaitForSeconds (2);
		Debug.Log("End waiting.");
		readyForNext = true;
//		ReadFile ();
	}


	// Generation of Objects ---> Should be better way to implement
	public static void CreateObjects(List<string> TimeStep)
	{
		for (int i = 0; i < (TimeStep.Count); i += 4) {

			Debug.Log (TimeStep [i]);

			// Handle Nucleosome Creation
			if (TimeStep [i] == "Nucleosome") {
				int Position = Convert.ToInt32 (TimeStep [i + 2]);
				int Length = Convert.ToInt32 (TimeStep [i + 3]);

				Position += Length / 2;			// TERRIBLE!!! Just use to DEMONSTRATE spacing ---> Delete and replace

				GameObject Nucleosome;

				Nucleosome = GameObject.CreatePrimitive (PrimitiveType.Sphere);
				Nucleosome.transform.position = new Vector3 (Position / 3, 0, 0);
				Nucleosome.transform.localScale = new Vector3 (Length / 3, 1, 1);		// Scale extends on both sides, so is a bad ultimate choice

				Nucleosome.tag = "Nucleosome";
		

				if (TimeStep [i + 1] == "Binding") {
					Nucleosome.gameObject.renderer.material.color = new Color (250, 0, 0);
				} else if (TimeStep [i + 1] == "Unbinding") {
					Nucleosome.gameObject.renderer.material.color = new Color (0, 250, 0);
				} else {
					Nucleosome.gameObject.renderer.material.color = new Color (0, 0, 250);
				}

			}


			// Handle Transcription Factor Creation
			if (TimeStep [i] == "Transcription_Factor") {
				int Position = Convert.ToInt32 (TimeStep [i + 2]);
				int Length = Convert.ToInt32 (TimeStep [i + 3]);

				Position += Length / 2;			// TERRIBLE!!! Just use to DEMONSTRATE spacing ---> Delete and replace		

				GameObject TranscriptionFactor;

				TranscriptionFactor = GameObject.CreatePrimitive (PrimitiveType.Cube);
				TranscriptionFactor.transform.position = new Vector3 (Position / 3, 0, 0);
				TranscriptionFactor.transform.localScale = new Vector3 (Length / 3, 1, 1);

				TranscriptionFactor.tag = "TranscriptionFactor";

				if (TimeStep [i + 1] == "REB1") {
					TranscriptionFactor.gameObject.renderer.material.color = new Color (250, 0, 10);
				} else if (TimeStep [i + 1] == "TBP") {
					TranscriptionFactor.gameObject.renderer.material.color = new Color (250, 10, 0);
				} else {
					TranscriptionFactor.gameObject.renderer.material.color = new Color (250, 20, 5);
				}
			}


			// Handle Transcriptional Machinery
			if (TimeStep [i] == "Transcriptional_Machinery") {
				int Position = Convert.ToInt32 (TimeStep [i + 2]);
				int Length = Convert.ToInt32 (TimeStep [i + 3]);

				Position += Length / 2;			// TERRIBLE!!! Just use to DEMONSTRATE spacing ---> Delete and replace

				GameObject TranscriptionalMachinery;

				TranscriptionalMachinery = GameObject.CreatePrimitive (PrimitiveType.Cylinder);
				TranscriptionalMachinery.transform.position = new Vector3 (Position / 3, 0, 0);
				TranscriptionalMachinery.transform.localScale = new Vector3 (Length / 3, 1, 1);

				TranscriptionalMachinery.tag = "TranscriptionalMachinery";

				if (TimeStep [i + 1] == "Init0" || TimeStep [i + 1] == "Init1") {
					TranscriptionalMachinery.gameObject.renderer.material.color = new Color (50, 50, 150);
				} else {
					TranscriptionalMachinery.gameObject.renderer.material.color = new Color (50, 150, 50);
				}

			}
		}
	}

	// Reads in a string (a timestep) with format [(type, subtype, position, length), (type, subtype, position, length)...].
	// It takes each component (type, subtype, position, length) and separates out the components into a list of strings called 'IntermediateArray'.
	public static List<string> read_time_step(string input)
	{
		string pattern = @"\(((.*?))\)";
		string intermediateString1 = "";
		string[] IntermediateArray = (intermediateString1).Split (new Char[] {' '});
		List<string> ObjectList;

		ObjectList = new List<string> ();

		foreach(Match match in Regex.Matches(input, pattern, RegexOptions.IgnoreCase))
		{
			intermediateString1 = Regex.Replace(match.Value, "[.,()]?", "");

			IntermediateArray = (intermediateString1).Split (new Char[] {' '});
			ObjectList.AddRange (IntermediateArray);

		}	
			
		readyForNext = false;
		return ObjectList;

	}

	public static void InitialTimestep()
	{
		// Use stream object to open and read file
		StreamReader inputFile = File.OpenText ("test3.txt");

		//string 'buffer' used to hold streamed 
		string read = null;

		//*************PARSING LOGIC************//

		// The current Timestep
		int j = 1;
		var TimeStepList = new List<string>();

		read = inputFile.ReadLine ();		// Remove while statement, and this reads the first line only

		Debug.Log (String.Format("TimestepList {0}", j));
		TimeStepList = read_time_step (read);

		Debug.Log (TimeStepList [0]);

		CreateObjects (TimeStepList);


		j++;



		//**************************************//*

		inputFile.Close();
	}



	public static void ReadFile()
	{


		// Use stream object to open and read file
		StreamReader inputFile = File.OpenText ("test3.txt");

		//string 'buffer' used to hold streamed 
		string read = null;

		//*************PARSING LOGIC************//

		// The current Timestep
		int j = 1;
		var TimeStepList = new List<string>();



		while((read = inputFile.ReadLine()) != null)		//Reads the whole line
		{
		
			DestroyObjects ();

			Debug.Log (String.Format("TimestepList {0}", j));
			TimeStepList = read_time_step (read);

			Debug.Log (TimeStepList [0]);

			CreateObjects (TimeStepList);

			DoCoroutine ();

//			Debug.Log("Time for next timestep.");

//			if (readyForNext == false)
//			{
//				return;
//			}
//


			j++;

//			DestroyObjects ();

		}

		//**************************************//*

		inputFile.Close();
	}




}
