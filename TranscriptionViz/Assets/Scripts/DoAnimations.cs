using UnityEngine;
using System.Collections;
using System;
using System.Collections.Generic;

public class DoAnimations : MonoBehaviour
{


		public List<InstructionObject> listIO = new List<InstructionObject>();
		public List<InstructionObject> listIO2 = new List<InstructionObject>();

		public List<InstructionObject> listIO3 = new List<InstructionObject> ();	

		public LinkedList<List<InstructionObject>> ll = new LinkedList<List<InstructionObject>>();

	  	public LinkedListNode<List<InstructionObject>> cursor;


		public IEnumerator parseList ()
		{
			ObjectsOnDNA one = new ObjectsOnDNA("Transcription_Factor", "MCM1", 5, 5);
			ObjectsOnDNA two = new ObjectsOnDNA("Transcription_Factor", "REB1", 10, 5);
			ObjectsOnDNA three = new ObjectsOnDNA("Transcription_Factor", "REB1", 15, 5);
			ObjectsOnDNA four = new ObjectsOnDNA("Nucleosome", "Binding", 20, 5);
			ObjectsOnDNA five = new ObjectsOnDNA("Transcriptional_Machinery", "Crick", 5, 5);
//			ObjectsOnDNA six = new ObjectsOnDNA("Transcriptional_Machinery", "Crick", 40, 5);

			InstructionObject IO1 = new InstructionObject(five, "CreateTranscriptionalMachinery");
			InstructionObject IO2 = new InstructionObject(one, "1,2,3");
			InstructionObject IO3 = new InstructionObject(two, "two");
			InstructionObject IO4 = new InstructionObject(three, "CreateTranscriptionFactor");
			InstructionObject IO5 = new InstructionObject(four, "CreateNucleosome");
			InstructionObject IO6 = new InstructionObject(four, "20, 0, 0");
			InstructionObject IO7 = new InstructionObject(three, "40, 0, 0");
			InstructionObject IO8 = new InstructionObject(five, "10, 0, 0");
			InstructionObject IO9 = new InstructionObject(five, "35, 0, 0");
			InstructionObject I11 = new InstructionObject(four, "10, 0, 0");


			InstructionObject I10 = new InstructionObject(five, "JustWait");

			
			listIO.Add(IO1);
			listIO.Add(IO2);
			listIO.Add(IO3);
			listIO.Add(IO4);
			listIO.Add(IO5);
			listIO.Add(IO6);
			listIO.Add(IO7);
			listIO.Add(IO8);
			
			listIO2.Add(IO9);
			listIO2.Add (I11);

			listIO3.Add (I10);
			
			ll.AddFirst(listIO);
			ll.AddLast (listIO3);
			ll.AddLast (listIO2);
	
			cursor = ll.First;


			while(cursor != null)
			{

//			yield return StartCoroutine_Auto (TimeStep.instance.JustWait ());

			foreach(InstructionObject current in cursor.Value)
				{
					//Create TF
					if (current.instruction == "CreateTranscriptionFactor")
					{
						yield return TranscriptionFactorClass.CreateTranscriptionFactor(current.TranscriptionSimObject);
					}
					
					//Create Nucleosome
					if(current.instruction == "CreateNucleosome")
					{
						yield return NucleosomeClass.CreateNucleosome(current.TranscriptionSimObject);
					}
					
					//Create TM
					if (current.instruction == "CreateTranscriptionalMachinery")
					{
						yield return TranscriptionalMachineryClass.CreateTranscriptionalMachinery(current.TranscriptionSimObject);
					}
					
					//Delete ObjectsOnDNA
					if(current.instruction == "Delete")
					{
						Debug.Log("Here " + current.TranscriptionSimObject.MainType);
						ObjectsOnDNA.DeleteObject(current.TranscriptionSimObject);
						yield return 0;
					}
					
					//Move Handling
					else if (current.instruction.Contains(","))
					{
//					yield return StartCoroutine_Auto (TimeStep.instance.JustWait ());
						
					yield return StartCoroutine(move(current));
						
					}	

				if (current.instruction == "JustWait")
				{
					Debug.Log("KNOWS TO WAIT");
					yield return TimeStep.instance.JustWait ();
					Debug.Log("TRIED TO WAIT");
				}


			}

			cursor = cursor.Next;
				
			}
		}
		
		
		
		public IEnumerator move(InstructionObject moveMe)
		{
			
//			yield return StartCoroutine_Auto (TimeStep.instance.JustWait ());

			//Extract coordinates and place into xyz array
			int[] xyz = new int[3];
			int index = 0;
			foreach(string j in moveMe.instruction.Split(','))
			{
				xyz[index] = Convert.ToInt32(j);
				index++;
			}
		
			GameObject[] nucleosomes = GameObject.FindGameObjectsWithTag ("Nucleosome");
			GameObject[] transcriptionFactors = GameObject.FindGameObjectsWithTag("TranscriptionFactor");
			GameObject[] transcriptionalMachineries = GameObject.FindGameObjectsWithTag("TranscriptionalMachinery");
		
			float convertPos = (moveMe.TranscriptionSimObject.StartPosition / 3.5f) - .6f;
		
			//Nucleosome move handling
			if(moveMe.TranscriptionSimObject.MainType == "Nucleosome")
			{
				foreach(GameObject nuc in nucleosomes)
				{
					if(convertPos == nuc.transform.position.x)
					{
						iTween.MoveTo(nuc, iTween.Hash("x", xyz[0], "time", 5));
					}
				}
			}
		
			//Transcription Factor move handling 
			if(moveMe.TranscriptionSimObject.MainType == "Transcription_Factor")
			{
				foreach(GameObject tf in transcriptionFactors)
				{
					if(convertPos == tf.transform.position.x)
					{
						iTween.MoveTo(tf, iTween.Hash("x", xyz[0], "time", 5));
					}
				}
			}
		
			//Transcriptional Machinery move handling
			if(moveMe.TranscriptionSimObject.MainType == "Transcriptional_Machinery")
			{
				Debug.Log("TM Start: " + convertPos);
				foreach(GameObject tm in transcriptionalMachineries)
				{
					Debug.Log("list of tms: " + tm.transform.position);
					if(convertPos == tm.transform.position.x)
					{
						Debug.Log("positions equal");
						
						yield return StartCoroutine(iTweenCmd(tm, xyz[0]));
						TimeStep.instance.JustWait ();
						
						Debug.Log("new pos: " + tm.transform.position);
						
						moveMe.TranscriptionSimObject.StartPosition = xyz[0];
					
					}
				}
				yield return null;
			}
		}
		
		public IEnumerator iTweenCmd(GameObject tweenMe, int x)
		{
			iTween.MoveTo(tweenMe, iTween.Hash("x", x, "time", 5));
			tweenMe.transform.position = new Vector3((x / 3.5f) - .6f, 0, 0);
			yield return new WaitForSeconds(5);
		}

		// Use this for initialization
		void Start ()
		{
//			StartCoroutine_Auto(parseList());
			
		}
			

			//ObjectsOnDNA TF  = new ObjectsOnDNA("Transcription_Factor", "REB1", 100, 5);
			//InstructionObject IO = new InstructionObject(TF, move);

			//iTween.MoveTo(chadobj, iTween.Hash("x", xyz[0], "y", xyz[1], "z", xyz[2], "time", 5));
			//IO.TranscriptionSimObject.transform.position += new Vector3(xyz[0], xyz[1], xyz[2]);

				
		

		// Update is called once per frame
		void Update ()
		{
		if (Input.GetKeyDown("space")) {
			StartCoroutine_Auto(parseList());
		}	

			
		}
		
}
