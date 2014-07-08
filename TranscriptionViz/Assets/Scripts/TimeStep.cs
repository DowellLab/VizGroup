﻿using UnityEngine;
using System.Collections;
using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.Reflection;
using System.Linq;
#if UNITY_EDITOR
using UnityEditor;
#endif

public class TimeStep : MonoBehaviour
{

	static public TimeStep instance;
	public bool isPaused = false;


	void Awake()
	{
		instance = this;
		QualitySettings.vSyncCount = 0;
		Application.targetFrameRate = 500;
	}


	// Implement waiting
	public IEnumerator JustWait()
	{
		yield return new WaitForSeconds (0.5f);
	}



	//Implement Destruction of Objects
	public static void DestroyObjects()
	{
		GameObject[] nucleosomes = GameObject.FindGameObjectsWithTag ("Nucleosome");
		GameObject[] transcriptionFactors = GameObject.FindGameObjectsWithTag("TranscriptionFactor");
		GameObject[] transcriptionalMachineries = GameObject.FindGameObjectsWithTag("TranscriptionalMachinery");

		foreach (GameObject go in nucleosomes)
		{
			if (go.name == "Nucleosome") {
				Destroy (go);
			}
		}

		foreach (GameObject go in transcriptionFactors)
		{
			if (go.name == "TranscriptionFactor") {
				Destroy (go);
			}
		}

		foreach (GameObject go in transcriptionalMachineries)
		{
			if (go.name == "TranscriptionalMachinery") {
				Destroy (go);
			}
		}
			
	}



	// Generation of Objects ---> Should be better way to implement
	public static IEnumerator CreateObjects(List<string> TimeStep)
	{

		// Call DestroyObjects first
		DestroyObjects ();


		// Then Create New Objects
		for (int i = 0; i < (TimeStep.Count); i += 4) {

			Debug.Log (TimeStep [i]);

			if (TimeStep [i] == "Nucleosome") {
			
				NucleosomeClass AwesomeObject = new NucleosomeClass (TimeStep [i + 1], Convert. ToInt64 (TimeStep [i + 2]), Convert. ToInt64 (TimeStep [i + 3]));
				Debug.Log (AwesomeObject.StartPosition);

				GameObject OurSpecialNucleosome = NucleosomeClass.CreateNucleosome (TimeStep [i + 1], Convert.ToInt64 (TimeStep [i + 2]), Convert.ToInt64 (TimeStep [i + 3]));

				yield return OurSpecialNucleosome;

//				yield return instance.StartCoroutine_Auto (instance.JustWait ());

			}
				
			if (TimeStep [i] == "Transcription_Factor") {

				GameObject OurSpecialTransFactor = TranscriptionFactorClass.CreateTranscriptionFactor (TimeStep [i + 1], Convert.ToInt64 (TimeStep [i + 2]), Convert.ToInt64 (TimeStep [i + 3]));

				yield return OurSpecialTransFactor;

//				yield return instance.StartCoroutine_Auto (instance.JustWait ());

			}
				
			if (TimeStep [i] == "Transcriptional_Machinery") {
			
				GameObject OurSpecialTransMach = TranscriptionalMachineryClass.CreateTranscriptionalMachinery (TimeStep [i + 1], Convert.ToInt64 (TimeStep [i + 2]), Convert.ToInt64 (TimeStep [i + 3]));


				yield return OurSpecialTransMach;
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
			
//		readyForNext = false;
		return ObjectList;

	}

	public IEnumerator InitialTimestep()
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

//		Debug.Log (String.Format("TimestepList {0}", j));
		TimeStepList = read_time_step (read);

//		Debug.Log (TimeStepList [0]);

		yield return StartCoroutine_Auto (CreateObjects (TimeStepList));

//		yield return StartCoroutine_Auto (AnimateObjects ());


		j++;



		//**************************************//*

		inputFile.Close();
	}



	public IEnumerator ReadFile()
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
		
			if (j == 1) {
			
				j++;

			} else {

//				yield return StartCoroutine_Auto (AnimateObjects ());

//				yield return StartCoroutine_Auto (JustWait ());

//				Debug.Log (String.Format ("TimestepList {0}", j));
				TimeStepList = read_time_step (read);

//				Debug.Log (TimeStepList [0]);

				yield return StartCoroutine_Auto (CreateObjects (TimeStepList));
			
				j++;

				yield return StartCoroutine_Auto (JustWait ());

//				yield return StartCoroutine_Auto (JustWait ());

			}



		}

		if (read == null) {
			Debug.Log("END OF FILE");
			VizGeneration.finished = true;
		}

		//**************************************//*

		inputFile.Close();

	}


	public IEnumerator AnimateObjects()
	{

		GameObject[] nucleosomes = GameObject.FindGameObjectsWithTag ("Nucleosome");
		GameObject[] transcriptionFactors = GameObject.FindGameObjectsWithTag("TranscriptionFactor");
		GameObject[] transcriptionalMachineries = GameObject.FindGameObjectsWithTag("TranscriptionalMachinery");

		foreach (GameObject go in nucleosomes)
		{
			iTween.MoveTo (go, new Vector3 (0, 50, 25), 5);
			yield return 0;
		}

		foreach (GameObject go in transcriptionFactors)
		{
			iTween.MoveTo (go, new Vector3 (0, 50, 25), 5);
			yield return 0;
		}

		foreach (GameObject go in transcriptionalMachineries)
		{
			iTween.MoveTo (go, new Vector3 (0, 50, 25), 5);
			yield return 0;
		}

	}


	public void PauseTimeStep()
	{
		isPaused = true;
		Time.timeScale = 0;
	}

	public void UnpauseTimeStep()
	{
		Time.timeScale = 1;
		isPaused = false;
	}

		
}
