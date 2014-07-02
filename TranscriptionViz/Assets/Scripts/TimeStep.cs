using UnityEngine;
using System.Collections;
using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.Reflection;
using System.Linq;
using UnityEditor;


public class Nucleosome
{
	public string Subtype;
	public float StartPosition;
	public float Length;

	public static Shader specular = Shader.Find("Specular");

	public Nucleosome(string subtype, float startPosition, float length)
	{
		Subtype = subtype;
		StartPosition = startPosition;
		Length = length;

	}


	public static GameObject CreateNucleosome(string Subtype, float StartPosition, float Length)
	{
	
		GameObject NewNucleosome;

		NewNucleosome = GameObject.CreatePrimitive (PrimitiveType.Sphere);

		if (StartPosition != 0) {
			NewNucleosome.transform.localScale = new Vector3 (Length / 3.5f, Length / 6f, Length / 3.5f); // Scale extends on both sides, so is a bad ultimate choice
		} else {
			NewNucleosome.transform.localScale = new Vector3 (Length / 3.5f, Length / 3f, Length / 3.5f);
		}

		NewNucleosome.renderer.material.shader = specular;

		StartPosition += Length / 4;
		NewNucleosome.transform.position = new Vector3 ((StartPosition / 3.5f) - 0.6f, 0.3f, 0);

//		NewNucleosome.transform.position = new Vector3 (10, -25, 0);

		NewNucleosome.name = "Nucleosome";
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
	

//		iTween.MoveTo (NewNucleosome, new Vector3 ((StartPosition/3), 0, 0), 2);



		return NewNucleosome;
	}

}


public class TranscriptionFactor
{

	public string Subtype;
	public float StartPosition;
	public float Length;
	public static Shader specular = Shader.Find("Specular");

	public TranscriptionFactor(string subtype, float startPosition, float length)
	{
		Subtype = subtype;
		StartPosition = startPosition;
		Length = length;

	}

	public static GameObject CreateTranscriptionFactor(string Subtype, float StartPosition, float Length)
	{
		GameObject NewTranscriptionFactor;
		NewTranscriptionFactor = GameObject.CreatePrimitive (PrimitiveType.Cube);
		NewTranscriptionFactor.transform.localScale = new Vector3 (Length / 3.5f, Length / 5, Length / 5);		// Scale extends on both sides, so is a bad ultimate choice
		NewTranscriptionFactor.renderer.material.shader = specular;

		StartPosition += Length / 3.5f;

		NewTranscriptionFactor.transform.position = new Vector3 ((StartPosition / 3.5f) - 0.6f, 0.3f, 0);

//		NewTranscriptionFactor.transform.position = new Vector3 (15, -25, 0);

		NewTranscriptionFactor.name = "TranscriptionFactor";
		NewTranscriptionFactor.tag = "TranscriptionFactor";


		// Transcription Factor Color
		if (Subtype == "REB1")
		{
			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (250, 0, 10);

		} else if (Subtype == "TBP") {

			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (250, 10, 0);

		} else {

			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (100, 20, 0);
		}


//		iTween.MoveTo (NewTranscriptionFactor, new Vector3 ((StartPosition/3), 0, 0), 2);



		return NewTranscriptionFactor;
	}

}

public class TranscriptionalMachinery
{
//	static int speed = 300;

	public string Subtype;
	public float StartPosition;
	public float Length;

	public TranscriptionalMachinery(string subtype, float startPosition, float length)
	{
		Subtype = subtype;
		StartPosition = startPosition;
		Length = length;

	}

	public static GameObject CreateTranscriptionalMachinery(string Subtype, float StartPosition, float Length)
	{
		GameObject NewTranscriptionalMachinery;
		NewTranscriptionalMachinery = GameObject.CreatePrimitive (PrimitiveType.Cylinder);
		NewTranscriptionalMachinery.transform.localScale = new Vector3 (Length / 3.5f, Length / 5, Length / 5);		// Scale extends on both sides, so is a bad ultimate choice
		NewTranscriptionalMachinery.renderer.material.shader = Shader.Find("Specular");

		StartPosition += Length / 3.5f;

		NewTranscriptionalMachinery.transform.position = new Vector3 ((StartPosition / 3.5f) - 0.6f, 0.3f, 0);

		NewTranscriptionalMachinery.name = "TranscriptionalMachinery";
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
			
//				Nucleosome AwesomeObject = new Nucleosome (TimeStep [i + 1], Convert. ToInt64 (TimeStep [i + 2]), Convert. ToInt64 (TimeStep [i + 3]));
//				Debug.Log (AwesomeObject.StartPosition);

				GameObject OurSpecialNucleosome = Nucleosome.CreateNucleosome (TimeStep [i + 1], Convert.ToInt64 (TimeStep [i + 2]), Convert.ToInt64 (TimeStep [i + 3]));

				yield return OurSpecialNucleosome;

//				yield return instance.StartCoroutine_Auto (instance.JustWait ());

			}
				
			if (TimeStep [i] == "Transcription_Factor") {

				GameObject OurSpecialTransFactor = TranscriptionFactor.CreateTranscriptionFactor (TimeStep [i + 1], Convert.ToInt64 (TimeStep [i + 2]), Convert.ToInt64 (TimeStep [i + 3]));

				yield return OurSpecialTransFactor;

//				yield return instance.StartCoroutine_Auto (instance.JustWait ());

			}
				
			if (TimeStep [i] == "Transcriptional_Machinery") {
			
				GameObject OurSpecialTransMach = TranscriptionalMachinery.CreateTranscriptionalMachinery (TimeStep [i + 1], Convert.ToInt64 (TimeStep [i + 2]), Convert.ToInt64 (TimeStep [i + 3]));


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
