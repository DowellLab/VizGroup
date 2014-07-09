using UnityEngine;
using System.Collections;
using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.Reflection;
using System.Linq;
using System.Xml.Linq;


#if UNITY_EDITOR
using UnityEditor;
#endif

public class TimeStep : MonoBehaviour
{

	static public TimeStep instance;
	public bool isPaused = false;
	static public int lineCount = 0;
	public int k = 0;

	public static int objectsInTimestep;


	private static int numberTimeSteps = CountLinesInFile ("test3.txt");



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


	public static int CountLinesInFile(string f)
	{
		using (StreamReader r = new StreamReader(f))
		{
			while (r.ReadLine() != null)
			{
				lineCount++;
			}
		}
		return lineCount;

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

//			Debug.Log (TimeStep [i]);

			if (TimeStep [i] == "Nucleosome") {
			
//				NucleosomeClass AwesomeObject = new NucleosomeClass (TimeStep [i + 1], Convert. ToInt64 (TimeStep [i + 2]), Convert. ToInt64 (TimeStep [i + 3]));
//				Debug.Log (AwesomeObject.StartPosition);

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
		List<string> ObjectList = new List<string> ();

		foreach(Match match in Regex.Matches(input, pattern, RegexOptions.IgnoreCase))
		{
			intermediateString1 = Regex.Replace(match.Value, "[.,()]?", "");

			IntermediateArray = (intermediateString1).Split (new Char[] {' '});
			ObjectList.AddRange (IntermediateArray);

		}	
			
//		readyForNext = false;

		objectsInTimestep = (ObjectList.Count) / 4;

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
		var timeStepList = new List<string>();

		read = inputFile.ReadLine ();		// Remove while statement, and this reads the first line only

//		Debug.Log (String.Format("timestepList {0}", j));
		timeStepList = read_time_step (read);

//		Debug.Log (timeStepList [0]);

		yield return StartCoroutine_Auto (CreateObjects (timeStepList));

//		yield return StartCoroutine_Auto (AnimateObjects ());


		j++;



		//**************************************//*

		inputFile.Close();
	}



	public IEnumerator ReadFile(int selectTimeStep)
	{

		// Add all lines of TimeStep file into new List
		List<string> allTimeSteps = System.IO.File.ReadAllLines("test3.txt").ToList();
//		Debug.Log (allTimeSteps [32]);

		// Number of TimeSteps


		//*************PARSING LOGIC************//

		// The current Timestep
		var timeStepList = new List<string>();

		// Next Timestep
		var lookForwardOne = new List<string> (); 

		for (k = selectTimeStep; k < (numberTimeSteps + 1); k++)
		{

//			yield return StartCoroutine_Auto (AnimateObjects ());
//
//			yield return StartCoroutine_Auto (JustWait ());

			timeStepList = read_time_step (allTimeSteps [k - 1]);

			if (k < numberTimeSteps) 
			{
				lookForwardOne = read_time_step (allTimeSteps [k]);
				int helloTest = 0;

				// Seems to be accurately comparing the two timesteps, checking if the first object of the current timestep is identical in the next timestep
				while (helloTest < objectsInTimestep * 4)
				{
					if ((timeStepList [0] == lookForwardOne [helloTest]) && (timeStepList [1] == lookForwardOne [helloTest + 1])
						&& (timeStepList [2] == lookForwardOne [helloTest + 2]) && (timeStepList [3] == lookForwardOne [helloTest + 3])) 
					{
						Debug.Log ("BINGO!!!");
					}
					helloTest += 4;

				}
			}
		
//			timeStepList = read_time_step (allTimeSteps [k - 1]);

			yield return StartCoroutine_Auto (CreateObjects (timeStepList));

			yield return StartCoroutine_Auto (JustWait ());

//			yield return StartCoroutine_Auto (JustWait ());

			if (k == numberTimeSteps)
			{
//				Debug.Log("END OF FILE");
				VizGeneration.finished = true;
				k = selectTimeStep;
				break;
			}

		}


			
	}

	public static void SimFinished()
	{

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
