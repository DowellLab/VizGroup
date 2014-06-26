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
//	static int speed = 10;

	public string Subtype;

	public int StartPosition;

	public int Length;

	public GameObject CreateNucleosome(Nucleosome nucleosome)
	{
		GameObject NewNucleosome;
		NewNucleosome = GameObject.CreatePrimitive (PrimitiveType.Sphere);
		NewNucleosome.transform.localScale = new Vector3 (nucleosome.Length / 3, nucleosome.Length / 3, nucleosome.Length/3);		// Scale extends on both sides, so is a bad ultimate choice

		nucleosome.StartPosition += nucleosome.Length / 3;
		NewNucleosome.transform.position = new Vector3 ((nucleosome.StartPosition/3), 0, 0);

//		NewNucleosome.transform.position = new Vector3 ((nucleosome.StartPosition/3), 10, 0);

//		Vector3 endPosition = new Vector3((nucleosome.StartPosition/3) , 0, 0);

//		NewNucleosome.transform.position = Vector3.Lerp (NewNucleosome.transform.position, endPosition, speed * Time.deltaTime);

//		NewNucleosome.transform.position = new Vector3 (nucleosome.StartPosition / 3, 0, 0);
//		NewNucleosome.transform.Translate (Vector3.down * speed * Time.deltaTime);


		NewNucleosome.tag = "Nucleosome";


		// Nucleosome Color
		if (nucleosome.Subtype == "Binding")
		{
			NewNucleosome.gameObject.renderer.material.color = new Color (250, 0, 0);

		} else if (nucleosome.Subtype == "Unbinding") {

			NewNucleosome.gameObject.renderer.material.color = new Color (0, 250, 0);

		} else {

			NewNucleosome.gameObject.renderer.material.color = new Color (0, 0, 250);
		}

		return NewNucleosome;
	}
}

public class TranscriptionFactor
{
	static int speed = 300;

	public string Subtype;

	public int StartPosition;

	public int Length;

	public GameObject CreateTranscriptionFactor(TranscriptionFactor transcriptionFactor)
	{
		GameObject NewTranscriptionFactor;
		NewTranscriptionFactor = GameObject.CreatePrimitive (PrimitiveType.Cube);
		NewTranscriptionFactor.transform.localScale = new Vector3 (transcriptionFactor.Length / 3, transcriptionFactor.Length / 3, transcriptionFactor.Length/3);		// Scale extends on both sides, so is a bad ultimate choice

		transcriptionFactor.StartPosition += transcriptionFactor.Length / 3;


		NewTranscriptionFactor.transform.position = new Vector3 (0, -10, -20);

		Vector3 endPosition = new Vector3((transcriptionFactor.StartPosition/3) , 0, 0);

		NewTranscriptionFactor.transform.position = Vector3.Lerp (NewTranscriptionFactor.transform.position, endPosition, speed * Time.deltaTime);

		NewTranscriptionFactor.transform.position = new Vector3 (transcriptionFactor.StartPosition / 3, 0, 0);

		NewTranscriptionFactor.tag = "TranscriptionFactor";


		// Transcription Factor Color
		if (transcriptionFactor.Subtype == "REB1")
		{
			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (250, 0, 10);

		} else if (transcriptionFactor.Subtype == "TBP") {

			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (250, 10, 0);

		} else {

			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (200, 20, 5);
		}

		return NewTranscriptionFactor;
	}

}

public class TranscriptionalMachinery
{
	static int speed = 300;

	public string Subtype;

	public int StartPosition;

	public int Length;

	public GameObject CreateTranscriptionalMachinery(TranscriptionalMachinery transcriptionalMachinery)
	{
		GameObject NewTranscriptionalMachinery;
		NewTranscriptionalMachinery = GameObject.CreatePrimitive (PrimitiveType.Cylinder);
		NewTranscriptionalMachinery.transform.localScale = new Vector3 (transcriptionalMachinery.Length / 3, transcriptionalMachinery.Length / 3, transcriptionalMachinery.Length/3);		// Scale extends on both sides, so is a bad ultimate choice

		transcriptionalMachinery.StartPosition += transcriptionalMachinery.Length / 3;


		NewTranscriptionalMachinery.transform.position = new Vector3 (0, -10, -20);

		Vector3 endPosition = new Vector3((transcriptionalMachinery.StartPosition/3) , 0, 0);

		NewTranscriptionalMachinery.transform.position = Vector3.Lerp (NewTranscriptionalMachinery.transform.position, endPosition, speed * Time.deltaTime);

		NewTranscriptionalMachinery.transform.position = new Vector3 (transcriptionalMachinery.StartPosition / 3, 0, 0);

		NewTranscriptionalMachinery.tag = "TranscriptionalMachinery";


		// Transcription Factor Color
		if (transcriptionalMachinery.Subtype == "Init0" || transcriptionalMachinery.Subtype == "Init1")
		{
			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (100, 5, 50);

		} else {

			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (50, 100, 5);
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
		Application.targetFrameRate = 2;
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


	// Implement waiting


	public IEnumerator JustWait()
	{
		yield return new WaitForSeconds (0.5f);
	}


	// Generation of Objects ---> Should be better way to implement
	public static IEnumerator CreateObjects(List<string> TimeStep)
	{
		for (int i = 0; i < (TimeStep.Count); i += 4) {

			Debug.Log (TimeStep [i]);

			// Handle Nucleosome Creation
			if (TimeStep [i] == "Nucleosome") {

				Nucleosome TestNucleosome = new Nucleosome ();
				TestNucleosome.Subtype = TimeStep[i + 1];
				TestNucleosome.StartPosition = Convert.ToInt32 (TimeStep [i + 2]);
				TestNucleosome.Length = Convert.ToInt32 (TimeStep [i + 3]);


				yield return TestNucleosome.CreateNucleosome (TestNucleosome);

			}


			// Handle Transcription Factor Creation
			if (TimeStep [i] == "Transcription_Factor") {

				TranscriptionFactor TestTranscriptionFactor = new TranscriptionFactor ();
				TestTranscriptionFactor.Subtype = TimeStep[i + 1];
				TestTranscriptionFactor.StartPosition = Convert.ToInt32 (TimeStep [i + 2]);
				TestTranscriptionFactor.Length = Convert.ToInt32 (TimeStep [i + 3]);

				yield return TestTranscriptionFactor.CreateTranscriptionFactor (TestTranscriptionFactor);

			}


			// Handle Transcriptional Machinery
			if (TimeStep [i] == "Transcriptional_Machinery") {

				TranscriptionalMachinery TestTranscriptionalMachinery = new TranscriptionalMachinery();
				TestTranscriptionalMachinery.Subtype = TimeStep[i + 1];
				TestTranscriptionalMachinery.StartPosition = Convert.ToInt32 (TimeStep [i + 2]);
				TestTranscriptionalMachinery.Length = Convert.ToInt32 (TimeStep [i + 3]);

				yield return TestTranscriptionalMachinery.CreateTranscriptionalMachinery (TestTranscriptionalMachinery);
//				TestTranscriptionalMachinery.CreateTranscriptionalMachinery (TestTranscriptionalMachinery);

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



		// Could count number of lines in Input file
		// CALL UPDATE from ANOTHER method??
		// UPDATE HANDLES ANIMATION ONLY???

		while((read = inputFile.ReadLine()) != null)		//Reads the whole line
		{
		
			if (j == 1) {

				j++;

			} else {

				DestroyObjects ();

				Debug.Log (String.Format ("TimestepList {0}", j));
				TimeStepList = read_time_step (read);

				Debug.Log (TimeStepList [0]);

				yield return StartCoroutine_Auto (CreateObjects (TimeStepList));

				j++;

				yield return StartCoroutine_Auto (JustWait ());
				
				}
		}

		//**************************************//*

		inputFile.Close();

	}
		
}
