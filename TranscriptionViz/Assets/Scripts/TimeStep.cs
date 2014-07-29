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
using System.Threading;


#if UNITY_EDITOR
using UnityEditor;
#endif

public class TimeStep : MonoBehaviour
{
	/* PUBLIC VARIABLES */
	static public TimeStep instance;
	public bool isPaused = false;
	public static int lineCount = 0;
	// k = current timestep
	public int k = 0;

	// The current Timestep
	private static List<string> timeStepList = new List<string>();
	public static List<ObjectsOnDNA> ObjectsInCurrentTime; // = new List<ObjectsOnDNA> ();

	// Next Timestep
//	private static List<string> lookForwardOne = new List<string> (); 
	public static List<ObjectsOnDNA> ObjectsInFutureTime;

	// Timesteps Ahead
	public static List<ObjectsOnDNA> ObjectsTwoAhead;
	public static List<ObjectsOnDNA> ObjectsThreeAhead;

	// Instruction Object List
	public static List<InstructionObject> listOfInstructions;

	// TimeStep Linked List
	public static LinkedList<List<InstructionObject>> ourLinkedList;

	//Select current File
	public static string currentFile = "RealExampleTest.txt"; 



	/* PRIVATE VARIABLES */

	private static int numberTimeSteps = CountLinesInFile (currentFile);


	/* METHODS */

	void Awake()
	{
		instance = this;
		QualitySettings.vSyncCount = 0;
		Application.targetFrameRate = 500;

	}


	// Implements waiting
	public IEnumerator JustWait()
	{
		// 0.5f seconds
		yield return new WaitForSeconds (1.15f);
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

	
	public static IEnumerator CreateObjects(List<string> TimeStep, string whichTime)
	{

		var thisTime = new List<ObjectsOnDNA>();

		if (whichTime == "Current")
		{
			ObjectsInCurrentTime = new List<ObjectsOnDNA> ();
			thisTime = ObjectsInCurrentTime;


		} else if (whichTime == "Future") {
			ObjectsInFutureTime = new List<ObjectsOnDNA> ();
			thisTime = ObjectsInFutureTime;


		} else if (whichTime == "TwoAhead") {
			ObjectsTwoAhead = new List<ObjectsOnDNA> ();
			thisTime = ObjectsTwoAhead;

		} else if (whichTime == "ThreeAhead") {
			ObjectsThreeAhead = new List<ObjectsOnDNA> ();
			thisTime = ObjectsThreeAhead;

		}


		// Then Repopulate list for new timestep
		for (int i = 0; i < (TimeStep.Count); i += 4) {
		
			if (TimeStep [i] == "'Nucleosome'") {

				NucleosomeClass AwesomeNuc = new NucleosomeClass (TimeStep [i], TimeStep [i + 1], Convert.ToInt64 (TimeStep [i + 2]), Convert.ToInt64 (TimeStep [i + 3]));
				thisTime.Add (AwesomeNuc);
				yield return thisTime;

			} else if (TimeStep [i] == "'Transcription_Factor'") {

				TranscriptionFactorClass AwesomeTF = new TranscriptionFactorClass (TimeStep[i], TimeStep [i + 1], Convert. ToInt64 (TimeStep [i + 2]), Convert. ToInt64 (TimeStep [i + 3]));
				thisTime.Add (AwesomeTF);
				yield return thisTime;

			}else if (TimeStep [i] == "'Transcriptional_Machinery'") {


				TranscriptionalMachineryClass AwesomeTM = new TranscriptionalMachineryClass (TimeStep[i], TimeStep [i + 1], Convert. ToInt64 (TimeStep [i + 2]), Convert. ToInt64 (TimeStep [i + 3]));
				thisTime.Add (AwesomeTM);
				yield return thisTime;

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
		StreamReader inputFile = File.OpenText (currentFile);

		//string 'buffer' used to hold streamed 
		string read = null;

		//*************PARSING LOGIC************//

		// The current Timestep
		int j = 1;
//		var timeStepList = new List<string>();

		read = inputFile.ReadLine ();		// Remove while statement, and this reads the first line only

//		Debug.Log (String.Format("timestepList {0}", j));
		timeStepList = read_time_step (read);

//		Debug.Log (timeStepList [0]);

//		yield return StartCoroutine_Auto (CreateObjects (timeStepList));

//		yield return StartCoroutine_Auto (ParseObjects (ObjectsInCurrentTime, ObjectsInFutureTime));
//
//		yield return StartCoroutine_Auto (TempAni (listOfInstructions));

		yield return 0;

		j++;



		//**************************************//*

		inputFile.Close();
	}


	public IEnumerator ReadFile(int selectTimeStep)
	{

		// Add all lines of TimeStep file into new List
		List<string> allTimeSteps = System.IO.File.ReadAllLines(currentFile).ToList();

		// LINKED LIST TIME
		ourLinkedList = new LinkedList<List<InstructionObject>> ();



		//*************PARSING LOGIC************//

//		// The current Timestep
//		var timeStepList = new List<string>();
//
//		// Next Timestep
		var lookForwardOne = new List<string> (); 

		var lookForwardTwo = new List<string> ();
		var lookForwardThree = new List<string> ();

		for (k = selectTimeStep; k < (numberTimeSteps + 1); k++)
		{

			Debug.Log ("NEW TIMESTEP " + k);

			listOfInstructions = new List<InstructionObject> ();

//			yield return StartCoroutine_Auto (JustWait ());



			timeStepList = read_time_step (allTimeSteps [k - 1]);


			if (k < numberTimeSteps) 
			{
				lookForwardOne = read_time_step(allTimeSteps [k]);

			}

			if (k < numberTimeSteps - 1)
			{
				lookForwardTwo = read_time_step (allTimeSteps [k + 1]);
			}

			if (k < numberTimeSteps - 2)
			{
				lookForwardThree = read_time_step (allTimeSteps [k + 2]);
			}


			yield return StartCoroutine_Auto (CreateObjects (lookForwardThree, "ThreeAhead"));

			yield return StartCoroutine_Auto (CreateObjects (lookForwardTwo, "TwoAhead"));

			yield return StartCoroutine_Auto (CreateObjects (lookForwardOne, "Future"));

			yield return StartCoroutine_Auto (CreateObjects (timeStepList, "Current"));




			yield return StartCoroutine_Auto (ParseObjects (ObjectsInCurrentTime, ObjectsInFutureTime, ObjectsTwoAhead, ObjectsThreeAhead));

			yield return StartCoroutine_Auto (TempAni (listOfInstructions));


			// ADD FOR ANIMATIONS???
			yield return StartCoroutine_Auto (JustWait ());
//			yield return StartCoroutine_Auto (JustWait ());


			// ADD TO LINKED LIST
			ourLinkedList.AddLast (listOfInstructions);



			yield return StartCoroutine_Auto (JustWait ());

			if (k == numberTimeSteps)
			{
//				Debug.Log("END OF FILE");
				VizGeneration.finished = true;
				k = selectTimeStep;
				break;
			}

//			yield return StartCoroutine_Auto(DoublyLinkedList.AddToList (InstructionObject.InstructionList));

		}

			
	}



	//
	// CREATES INSTRUCTION LIST
	//
	public IEnumerator ParseObjects(List <ObjectsOnDNA> AnimateList, List <ObjectsOnDNA> lookAhead, List<ObjectsOnDNA> twoAhead, List<ObjectsOnDNA> threeAhead)
	{
	
		///
		/// HANDLES OBJECT CHANGES ---> MOVE, ALTER, DELETE
		///
		foreach (ObjectsOnDNA cool in AnimateList)
		{
			var found = false;

			if (k == VizGeneration.startStep)
			{
				if (cool.MainType == "'Nucleosome'")
				{
					InstructionObject initNucCreate = new InstructionObject (cool, "NucleosomeClass.CreateNucleosome");
					listOfInstructions.Add (initNucCreate);
				}

				if(cool.MainType == "'Transcription_Factor'")
				{
					InstructionObject initTFCreate = new InstructionObject (cool, "TranscriptionFactorClass.CreateTranscriptionFactor");
					listOfInstructions.Add (initTFCreate);
				}

				if(cool.MainType == "'Transcriptional_Machinery'")
				{
					InstructionObject initTMCreate = new InstructionObject (cool, "TranscriptionalMachineryClass.CreateTranscriptionalMachinery");
					listOfInstructions.Add (initTMCreate);
				}

			}



			if (cool.MainType == "'Nucleosome'")
			{

				foreach (ObjectsOnDNA tests in lookAhead) {
				
					if (cool.MainType == tests.MainType && cool.Subtype == tests.Subtype && cool.Length == tests.Length) {
						if(cool.StartPosition == tests.StartPosition)
						{
							found = true;
							Debug.Log("SAME NUCLEOSOME " + cool.StartPosition);

						} else if (Math.Abs(tests.StartPosition - cool.StartPosition) <= 10){
							found = true;
							Debug.Log ("Time to move" + cool.StartPosition + " to " + tests.StartPosition);

							var tempInt1 = tests.StartPosition;
							string tempString1 = tempInt1.ToString();

							InstructionObject moveNuc = new InstructionObject (cool, tempString1);
							listOfInstructions.Add (moveNuc);

						} else {
//							???
						}
					} else if (cool.MainType == tests.MainType && cool.Length == tests.Length)
					{

						if (cool.StartPosition == tests.StartPosition) {
							found = true;
							Debug.Log ("CHANGE NUCLEOSOME SUBTYPE TO " + tests.Subtype);

							InstructionObject changeNuc = new InstructionObject (cool, tests.Subtype);
							listOfInstructions.Add (changeNuc);

						} else if (Math.Abs(tests.StartPosition - cool.StartPosition) <= 10) {
							found = true;
							Debug.Log ("NUCLEOSOME MOVING AND CHANGING SUBTYPE");

							var tempInt2 = tests.StartPosition;
							string tempString2 = tempInt2.ToString();

							InstructionObject firstChangeNuc = new InstructionObject (cool, tests.Subtype);
							InstructionObject thenMoveNuc = new InstructionObject (cool, tempString2);
							listOfInstructions.Add (firstChangeNuc);
							listOfInstructions.Add (thenMoveNuc);
						}

					}

				}

				// HANDLING DELETION!!!
				if (!found)
				{
					var waitOnIt = false;

					foreach (ObjectsOnDNA wait in twoAhead)
					{
						if (cool.MainType == wait.MainType && cool.Subtype == wait.Subtype && Math.Abs(wait.StartPosition - cool.StartPosition) <= 10 && cool.Length == wait.Length)
						{
							waitOnIt = true;
						} else {
							foreach(ObjectsOnDNA longer in threeAhead)
							{
								if (cool.MainType == longer.MainType && cool.Subtype == longer.Subtype && Math.Abs(longer.StartPosition - cool.StartPosition) <= 10 && cool.Length == longer.Length)
								{
									waitOnIt = true;
								}
							}
						}
					}

					if (waitOnIt == false)
					{
						Debug.Log ("DELETE " + cool.MainType + " at position " + cool.StartPosition);

						InstructionObject delNuc = new InstructionObject (cool, "ObjectsOnDNA.DeleteObject");
						listOfInstructions.Add (delNuc);

					} else {

						Debug.Log ("Move it on up.");

						InstructionObject waitNuc = new InstructionObject (cool, "WAIT");
						listOfInstructions.Add (waitNuc);
					}


				}


			//
			// TF HANDLING
			//
			} else if (cool.MainType == "'Transcription_Factor'"){

				foreach (ObjectsOnDNA tests in lookAhead) {

					if (cool.MainType == tests.MainType && cool.Subtype == tests.Subtype && cool.Length == tests.Length) {
						if(cool.StartPosition == tests.StartPosition)
						{
							found = true;
							Debug.Log("SAME TF " + cool.StartPosition);
						} 
					}

				}

				// DELETION
				if (!found)
				{
					var waitOnIt = false;

					foreach (ObjectsOnDNA wait in twoAhead)
					{
						if (cool.MainType == wait.MainType && cool.Subtype == wait.Subtype && cool.StartPosition == wait.StartPosition && cool.Length == wait.Length)
						{
							waitOnIt = true;
						} else {
							foreach(ObjectsOnDNA longer in threeAhead)
							{
								if (cool.MainType == longer.MainType && cool.Subtype == longer.Subtype && cool.StartPosition == longer.StartPosition && cool.Length == longer.Length)
								{
									waitOnIt = true;
								}
							}
						}
					}

					if (waitOnIt == false)
					{
						Debug.Log ("DELETE " + cool.MainType + " at position " + cool.StartPosition);
						InstructionObject delTF = new InstructionObject (cool, "ObjectsOnDNA.DeleteObject");
						listOfInstructions.Add (delTF);

					} else {

						Debug.Log ("Move it on up.");

						InstructionObject waitTF = new InstructionObject (cool, "WAIT");
						listOfInstructions.Add (waitTF);
					}


				}



			//
			// TM HANDLING
			//
			} else if (cool.MainType == "'Transcriptional_Machinery'"){

				foreach (ObjectsOnDNA tests in lookAhead) {

					if (cool.MainType == tests.MainType && cool.Subtype == tests.Subtype && cool.Length == tests.Length) {
						if(cool.StartPosition == tests.StartPosition)
						{
							found = true;
							Debug.Log("SAME TM " + cool.StartPosition);
						} else if (Math.Abs(cool.StartPosition - tests.StartPosition) <= 3){
							found = true;
							Debug.Log ("MOVE TM" + cool.StartPosition + " to " + tests.StartPosition);

							var tempInt1 = tests.StartPosition;
							string tempString1 = tempInt1.ToString();

							InstructionObject moveTM = new InstructionObject (cool, tempString1);
							listOfInstructions.Add (moveTM);
						} 

					} else if (cool.MainType == tests.MainType && cool.Length == tests.Length)
					{
						if (cool.StartPosition == tests.StartPosition) 
						{
							found = true;
							Debug.Log ("CHANGE TM SUBTYPE TO " + tests.Subtype);

							InstructionObject changeTM = new InstructionObject (cool, tests.Subtype);
							listOfInstructions.Add (changeTM);
						} else if (Math.Abs(cool.StartPosition - tests.StartPosition) <= 3) {
							found = true;
							Debug.Log ("TM MOVING AND CHANGING SUBTYPE");

							var tempInt2 = tests.StartPosition;
							string tempString2 = tempInt2.ToString();

							InstructionObject firstChangeTM = new InstructionObject (cool, tests.Subtype);
							InstructionObject thenMoveTM = new InstructionObject (cool, tempString2);
							listOfInstructions.Add (firstChangeTM);
							listOfInstructions.Add (thenMoveTM);
						}

					}

				}

				// HANDLING DELETION!!!
				if (!found)
				{
					Debug.Log ("DELETE " + cool.MainType + " at position " + cool.StartPosition);
					InstructionObject delTM = new InstructionObject (cool, "ObjectsOnDNA.DeleteObject");
					listOfInstructions.Add (delTM);
				}

			}

		}


		///
		/// HANDLES OBJECT CREATION
		///
		foreach(ObjectsOnDNA tests in lookAhead)
		{
			var found = false;

			foreach(ObjectsOnDNA cool in AnimateList)
			{
				if (tests.MainType  == cool.MainType && cool.Subtype == tests.Subtype && cool.Length == tests.Length)
				{
					if (tests.MainType == "'Nucleosome'") {
						if (Math.Abs (cool.StartPosition - tests.StartPosition) <= 10) {
							found = true;
						}
					} else if (tests.MainType == "'Transcriptional_Machinery'")
					{
						if (cool.StartPosition == tests.StartPosition)
						{
							found = true;
						} else if (Math.Abs (cool.StartPosition - tests.StartPosition) <= 3) {
							found = true;
						}
					} else if (tests.MainType == "'Transcription_Factor'") {
						if(cool.StartPosition == tests.StartPosition){
							found = true;
						}

					}
				} else if (cool.Subtype != tests.Subtype && tests.MainType != "'Transcription_Factor'")
				{
					if (cool.MainType == tests.MainType && cool.StartPosition == tests.StartPosition && cool.Length == tests.Length)
					{
						found = true;
					}
				} 


				// IF MOVE AND SUBTYPE CHANGE
				if (cool.MainType == tests.MainType && cool.Length == tests.Length) 
				{
					if (cool.MainType == "'Nucleosome'")
					{
						if (Math.Abs(tests.StartPosition - cool.StartPosition) <= 10)
						{
							found = true;
						}
					} else if (cool.MainType == "'Transcriptional_Machinery'") {

						if (Math.Abs(cool.StartPosition - tests.StartPosition) <= 3)
						{
							found = true;
						}
					}
				}

			}

			if (!found)
			{
				Debug.Log ("CREATE " + tests.MainType + " at Position " + tests.StartPosition);

				if (tests.MainType == "'Nucleosome'")
				{
					InstructionObject nowCreate = new InstructionObject (tests, "NucleosomeClass.CreateNucleosome");
					listOfInstructions.Add (nowCreate);

				} else if (tests.MainType == "'Transcription_Factor'") {
					InstructionObject nowCreate = new InstructionObject (tests, "TranscriptionFactorClass.CreateTranscriptionFactor");
					listOfInstructions.Add (nowCreate);

				} else if (tests.MainType == "'Transcriptional_Machinery'") {
					InstructionObject nowCreate = new InstructionObject (tests, "TranscriptionalMachineryClass.CreateTranscriptionalMachinery");
					listOfInstructions.Add (nowCreate);
				}

			}
		}



		///
		/// RETURN LIST OF INSTRUCTIONS
		///

		yield return listOfInstructions;

	}
				

	// TEMPORARY HANDLING OF ANIMATION
	public IEnumerator TempAni(List <InstructionObject> toAnimate)
	{
		foreach (InstructionObject joe in toAnimate) {


			if (joe.instruction == "NucleosomeClass.CreateNucleosome")
			{
				NucleosomeClass.CreateNucleosome (joe.TranscriptionSimObject);
			} else if (joe.instruction == "TranscriptionFactorClass.CreateTranscriptionFactor" ) {
				TranscriptionFactorClass.CreateTranscriptionFactor (joe.TranscriptionSimObject);
			} else if (joe.instruction == "TranscriptionalMachineryClass.CreateTranscriptionalMachinery") {
				TranscriptionalMachineryClass.CreateTranscriptionalMachinery (joe.TranscriptionSimObject);
			}

			if (joe.instruction == "ObjectsOnDNA.DeleteObject" )
			{
				ObjectsOnDNA.DeleteObject (joe.TranscriptionSimObject);
			}

			if (joe.instruction.Contains("0") || joe.instruction.Contains("1") || joe.instruction.Contains("2") || 
				joe.instruction.Contains("3") || joe.instruction.Contains("4") || joe.instruction.Contains("5") ||
				joe.instruction.Contains("6") || joe.instruction.Contains("7") || joe.instruction.Contains("8") || 
				joe.instruction.Contains("9") ) 
			{
				float xPos = Convert.ToInt64 (joe.instruction);

				ObjectsOnDNA.MoveObject (joe.TranscriptionSimObject, xPos);
			}


			if (joe.instruction == "'Binding'" || joe.instruction == "'Unbinding'" || joe.instruction == "'Stable'")
			{
				ObjectsOnDNA.ChangeSubtype (joe.TranscriptionSimObject, joe.instruction);
			} else if (joe.instruction.Contains("Crick") || joe.instruction.Contains("Watson")) {
				ObjectsOnDNA.ChangeSubtype (joe.TranscriptionSimObject, joe.instruction);
			}

			if (joe.instruction == "WAIT")
			{
				ObjectsOnDNA.MakeWait (joe.TranscriptionSimObject);
			}



		}

		yield return 0;
	}




	public void PauseTimeStep()
	{
		isPaused = true;
		Time.timeScale = 0;
	}

	public void UnpauseTimeStep()
	{
		Time.timeScale = 8;
		isPaused = false;
	}

		
}
