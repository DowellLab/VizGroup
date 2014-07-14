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
	/* PUBLIC VARIABLES */
	static public TimeStep instance;
	public bool isPaused = false;
	public static int lineCount = 0;
	public int k = 0;

	// The current Timestep
	private static List<string> timeStepList = new List<string>();
	public static List<ObjectsOnDNA> ObjectsInCurrentTime = new List<ObjectsOnDNA> ();

	// Next Timestep
	private static List<string> lookForwardOne = new List<string> (); 
	public static List<ObjectsOnDNA> ObjectsInFutureTime = new List<ObjectsOnDNA> ();

	// Prev Timestep
	private static List<string> lookBackOne = new List<string> ();
	public static List<ObjectsOnDNA> ObjectsInPastTime = new List<ObjectsOnDNA> ();



	/* PRIVATE VARIABLES */
	private static int numberTimeSteps = CountLinesInFile ("test3.txt");


	/* METHODS */

	void Awake()
	{
		instance = this;
		QualitySettings.vSyncCount = 0;
		Application.targetFrameRate = 500;
	}


	/// <summary>
	/// Justs the wait.
	/// </summary>
	/// <returns>The wait.</returns>

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

	
	public static IEnumerator CreateObjects(List<string> TimeStep)
	{

		// Call DestroyObjects (first?)
		DestroyObjects ();

		// Add List to Node !!!!!!!!!!!


		// Clear list for repopulation
		ObjectsInCurrentTime.Clear();



		// Then Repopulate list for new timestep
		for (int i = 0; i < (TimeStep.Count); i += 4) {

//			Debug.Log (TimeStep [i]);

			if (TimeStep [i] == "Nucleosome") {
			
				NucleosomeClass AwesomeNuc = new NucleosomeClass (TimeStep[i],TimeStep [i + 1], Convert. ToInt64 (TimeStep [i + 2]), Convert. ToInt64 (TimeStep [i + 3]));


				if (TimeStep == timeStepList)
				{
					ObjectsInCurrentTime.Add (AwesomeNuc);

//					Debug.Log ("Added Nuc to Current");
//					Debug.Log (ObjectsInCurrentTime.Count);

					yield return ObjectsInCurrentTime;

				} else if (TimeStep == lookForwardOne){

					ObjectsInFutureTime.Add(AwesomeNuc);

					yield return ObjectsInFutureTime;


				} else if (TimeStep == lookBackOne) {

					ObjectsInPastTime.Add(AwesomeNuc);

					yield return ObjectsInPastTime;
				
				} else {

					yield return 0;
				}

			}
				
			if (TimeStep [i] == "Transcription_Factor") {

				TranscriptionFactorClass AwesomeTF = new TranscriptionFactorClass (TimeStep[i], TimeStep [i + 1], Convert. ToInt64 (TimeStep [i + 2]), Convert. ToInt64 (TimeStep [i + 3]));

				if (TimeStep == timeStepList)
				{
					ObjectsInCurrentTime.Add (AwesomeTF);

//					Debug.Log ("Added TF to Current");

					yield return ObjectsInCurrentTime;

				} else if (TimeStep == lookForwardOne){

					ObjectsInFutureTime.Add(AwesomeTF);
					yield return ObjectsInFutureTime;


				} else if (TimeStep == lookBackOne) {

					ObjectsInPastTime.Add(AwesomeTF);

					yield return ObjectsInPastTime;

				} else {

					yield return 0;
				}

			}
				
			if (TimeStep [i] == "Transcriptional_Machinery") {
			
				TranscriptionalMachineryClass AwesomeTM = new TranscriptionalMachineryClass (TimeStep[i], TimeStep [i + 1], Convert. ToInt64 (TimeStep [i + 2]), Convert. ToInt64 (TimeStep [i + 3]));

				if (TimeStep == timeStepList)
				{
					ObjectsInCurrentTime.Add (AwesomeTM);
//					Debug.Log ("Added TM to Current");

					yield return ObjectsInCurrentTime;

				} else if (TimeStep == lookForwardOne){

					ObjectsInFutureTime.Add(AwesomeTM);
					yield return ObjectsInFutureTime;


				} else if (TimeStep == lookBackOne) {

					ObjectsInPastTime.Add(AwesomeTM);

//					Debug.Log (ObjectsInPastTime);
					yield return ObjectsInPastTime;

				} else {

					yield return 0;
				}


//				GameObject OurSpecialTransMach = TranscriptionalMachineryClass.CreateTranscriptionalMachinery (TimeStep [i + 1], Convert.ToInt64 (TimeStep [i + 2]), Convert.ToInt64 (TimeStep [i + 3]));


//				yield return OurSpecialTransMach;
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

//		objectsInTimestep = (ObjectList.Count) / 4;

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

//		yield return StartCoroutine_Auto (AnimateObjects (ObjectsInCurrentTime));


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

//		// The current Timestep
//		var timeStepList = new List<string>();
//
//		// Next Timestep
//		var lookForwardOne = new List<string> (); 
//		var lookBackOne = new List<string> ();

		for (k = selectTimeStep; k < (numberTimeSteps + 1); k++)
		{

			Debug.Log ("NEW TIMESTEP " + k);
//
//			yield return StartCoroutine_Auto (JustWait ());

			if (k > 1)
			{
				lookBackOne = read_time_step (allTimeSteps[k - 2]);
			}


			timeStepList = read_time_step (allTimeSteps [k - 1]);


			if (k < numberTimeSteps) 
			{
				lookForwardOne = read_time_step(allTimeSteps [k]);
			}
		
//			timeStepList = read_time_step (allTimeSteps [k - 1]);

			yield return StartCoroutine_Auto (CreateObjects (timeStepList));

//			yield return StartCoroutine_Auto (JustWait ());

			yield return StartCoroutine_Auto (ParseObjects (ObjectsInCurrentTime));

			yield return StartCoroutine_Auto (JustWait ());

			if (k == numberTimeSteps)
			{
//				Debug.Log("END OF FILE");
				VizGeneration.finished = true;
				k = selectTimeStep;
				break;
			}



		}
			
	}



	public IEnumerator ParseObjects(List <ObjectsOnDNA> AnimateList)
	{
	
		foreach (ObjectsOnDNA cool in AnimateList)
		{
//			DestroyObjects ();
			if (cool.MainType == "Nucleosome")
			{
				InstructionObject NewInstruct = new InstructionObject (cool, "NucleosomeClass.CreateNucleosome");
				InstructionObject.CreateInstructList (NewInstruct);

				// Won't actually create objects here in the future ---> This is for debugging purposes only
				NucleosomeClass.CreateNucleosome (cool);

			} else if (cool.MainType == "Transcription_Factor"){

				InstructionObject NewInstruct = new InstructionObject (cool, "TranscriptionFactorClass.CreateTranscriptionFactor");
				InstructionObject.CreateInstructList (NewInstruct);

				TranscriptionFactorClass.CreateTranscriptionFactor (cool);
			} else if (cool.MainType == "Transcriptional_Machinery"){

				InstructionObject NewInstruct = new InstructionObject (cool, "TranscriptionalMachineryClass.CreateTranscriptionalMachinery");
				InstructionObject.CreateInstructList (NewInstruct);

				TranscriptionalMachineryClass.CreateTranscriptionalMachinery (cool);
			}
//			Debug.Log (cool.Subtype + " " + cool.StartPosition + " " + cool.Length);

		}

		// RETURN ANIMATION INSTRUCTIONS!!! A LIST ---> NOPE

		yield return AnimateList;


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
