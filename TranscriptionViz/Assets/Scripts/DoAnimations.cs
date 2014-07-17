using UnityEngine;
using System.Collections;
using System;
using System.Collections.Generic;

public class DoAnimations : MonoBehaviour
{

		public List<InstructionObject> listIO = new List<InstructionObject>();
		public LinkedList<List<InstructionObject>> ll = new LinkedList<List<InstructionObject>>();
		

		public IEnumerator parseList ()
		{
			ObjectsOnDNA one = new ObjectsOnDNA("Transcription_Factor", "MCM1", 5, 5);
			ObjectsOnDNA two = new ObjectsOnDNA("Transcription_Factor", "REB1", 10, 5);
			ObjectsOnDNA three = new ObjectsOnDNA("Transcription_Factor", "REB1", 15, 5);
			ObjectsOnDNA four = new ObjectsOnDNA("Nucleosome", "Binding", 20, 5);
			InstructionObject IO1 = new InstructionObject(one, "1,2,3");
			InstructionObject IO2 = new InstructionObject(two, "two");
			InstructionObject IO3 = new InstructionObject(three, "CreateTranscriptionFactor");
			InstructionObject IO4 = new InstructionObject(four, "CreateNucleosome");
			listIO.Add(IO1);
			listIO.Add(IO2);
			listIO.Add(IO3);
			listIO.Add(IO4);
			ll.AddFirst(listIO);
			LinkedListNode<List<InstructionObject>> cursor;
			cursor = ll.First;
			
			while(cursor != null)
			{
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
					
					//Delete ObjectsOnDNA
					if(current.instruction == "Delete")
					{
						yield return ObjectsOnDNA.DeleteObject(current.TranscriptionSimObject);
					}
					
					//Move Handling
					else if (current.instruction.Contains(","))
					{
						int[] xyz = new int[3];
						int index = 0;
						foreach(string j in current.instruction.Split(','))
						{
							xyz[index] = Convert.ToInt32(j);
							index++;
						}
						foreach(int i in xyz)
						{
							Debug.Log(i);
						}
					}

				}
				
				cursor = cursor.Next;
				
			}
		}
		

		// Use this for initialization
		void Start ()
		{
			StartCoroutine_Auto(parseList());
			
		}
			

			//ObjectsOnDNA TF  = new ObjectsOnDNA("Transcription_Factor", "REB1", 100, 5);
			//InstructionObject IO = new InstructionObject(TF, move);

			//iTween.MoveTo(chadobj, iTween.Hash("x", xyz[0], "y", xyz[1], "z", xyz[2], "time", 5));
			//IO.TranscriptionSimObject.transform.position += new Vector3(xyz[0], xyz[1], xyz[2]);

				
		
	
		// Update is called once per frame
		void Update ()
		{
			
		}
		
}
