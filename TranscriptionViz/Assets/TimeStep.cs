using UnityEngine;
using System.Collections;
using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.Reflection;
using System.Linq;


public class Nucleosome
{
	public static GameObject CreateNucleosome(string Subtype, int StartPosition, int Length)
	{
		GameObject NewNucleosome;

		NewNucleosome = GameObject.CreatePrimitive (PrimitiveType.Sphere);
		NewNucleosome.transform.localScale = new Vector3 (Length / 3, Length / 3, Length/3);		// Scale extends on both sides, so is a bad ultimate choice

		StartPosition += Length / 3;
		NewNucleosome.transform.position = new Vector3 ((StartPosition/3), 0, 0);

		NewNucleosome.tag = "Nucleosome";

		// Nucleosome Color
		if (Subtype == "Binding")
		{
			NewNucleosome.gameObject.renderer.material.color = new Color (250, 0, 0);
		
		} else if (Subtype == "Unbinding") {
		
			NewNucleosome.gameObject.renderer.material.color = new Color (0, 250, 0);

		} else {

			NewNucleosome.gameObject.renderer.material.color = new Color (0, 0, 250);
		}
	
		return NewNucleosome;
	}
}


public class TranscriptionFactor
{

	public static GameObject CreateTranscriptionFactor(string Subtype, int StartPosition, int Length)
	{
		GameObject NewTranscriptionFactor;
		NewTranscriptionFactor = GameObject.CreatePrimitive (PrimitiveType.Cube);
		NewTranscriptionFactor.transform.localScale = new Vector3 (Length / 3, Length / 3, Length/3);		// Scale extends on both sides, so is a bad ultimate choice

		StartPosition += Length / 3;

		NewTranscriptionFactor.transform.position = new Vector3 (StartPosition / 3, 0, 0);

		NewTranscriptionFactor.tag = "TranscriptionFactor";


		// Transcription Factor Color
		if (Subtype == "REB1")
		{
			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (250, 0, 10);

		} else if (Subtype == "TBP") {

			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (250, 10, 0);

		} else {

			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (100, 20, 5);
		}

		return NewTranscriptionFactor;
	}

}

public class TranscriptionalMachinery
{
//	static int speed = 300;

	public string Subtype;

	public int StartPosition;

	public int Length;

	public static GameObject CreateTranscriptionalMachinery(string Subtype, int StartPosition, int Length)
	{
		GameObject NewTranscriptionalMachinery;
		NewTranscriptionalMachinery = GameObject.CreatePrimitive (PrimitiveType.Cylinder);
		NewTranscriptionalMachinery.transform.localScale = new Vector3 (Length / 3, Length / 3, Length / 3);		// Scale extends on both sides, so is a bad ultimate choice

		StartPosition += Length / 3;

		NewTranscriptionalMachinery.transform.position = new Vector3 (StartPosition / 3, 0, 0);

		NewTranscriptionalMachinery.tag = "TranscriptionalMachinery";


		// Transcription Factor Color
		if (Subtype == "Init0" || Subtype == "Init1")
		{
			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (100, 0, 50);

		} else {

			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (50, 100, 0);
		}

		return NewTranscriptionalMachinery;
	}
}


public class TimeStep : MonoBehaviour
{

	static public TimeStep instance;

	void Awake()
	{
		instance = this;
		QualitySettings.vSyncCount = 0;
		Application.targetFrameRate = 200;
	}


	// Implement waiting
	public IEnumerator JustWait()
	{
		yield return new WaitForSeconds (1.75f);
	}



	//Implement Destruction of Objects
	public static void DestroyObjects()
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



	// Generation of Objects ---> Should be better way to implement
	public static IEnumerator CreateObjects(List<string> TimeStep)
	{
		for (int i = 0; i < (TimeStep.Count); i += 4) {

			Debug.Log (TimeStep [i]);

			// Handle Nucleosome Creation
			if (TimeStep [i] == "Nucleosome") {

				yield return Nucleosome.CreateNucleosome (TimeStep [i + 1], Convert.ToInt32 (TimeStep [i + 2]), Convert.ToInt32 (TimeStep [i + 3]));

			}


			// Handle Transcription Factor Creation
			if (TimeStep [i] == "Transcription_Factor") {
			
				yield return TranscriptionFactor.CreateTranscriptionFactor (TimeStep [i + 1], Convert.ToInt32 (TimeStep [i + 2]), Convert.ToInt32 (TimeStep [i + 3]));

			}


			// Handle Transcriptional Machinery
			if (TimeStep [i] == "Transcriptional_Machinery") {
			
				yield return TranscriptionalMachinery.CreateTranscriptionalMachinery (TimeStep [i + 1], Convert.ToInt32 (TimeStep [i + 2]), Convert.ToInt32 (TimeStep [i + 3]));

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

		Debug.Log (String.Format("TimestepList {0}", j));
		TimeStepList = read_time_step (read);

//		Debug.Log (TimeStepList [0]);

		yield return StartCoroutine_Auto (CreateObjects (TimeStepList));


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

				DestroyObjects ();

				Debug.Log (String.Format ("TimestepList {0}", j));
				TimeStepList = read_time_step (read);

//				Debug.Log (TimeStepList [0]);

				yield return StartCoroutine_Auto (CreateObjects (TimeStepList));

				j++;

				yield return StartCoroutine_Auto (JustWait ());
				
				}
		}

		//**************************************//*

		inputFile.Close();

	}
		
}
