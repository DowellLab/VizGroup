﻿using UnityEngine;
using System.Collections;
using System;
using System.Collections.Generic;

public class DoAnimations : MonoBehaviour
{


		public List<InstructionObject> listIO = new List<InstructionObject>();
		public LinkedList<List<InstructionObject>> ll = new LinkedList<List<InstructionObject>>();
		List<ObjectsOnDNA> objs  = new List<ObjectsOnDNA>();
//		LinkedList<List<ObjectsOnDNA>> mylist = new LinkedList<List<ObjectsOnDNA>>();

		public IEnumerator parseList ()
		{
			ObjectsOnDNA one = new ObjectsOnDNA("Transcription_Factor", "MCM1", 5, 5);
			ObjectsOnDNA two = new ObjectsOnDNA("Transcription_Factor", "REB1", 10, 5);
			ObjectsOnDNA three = new ObjectsOnDNA("Transcription_Factor", "REB1", 15, 5);
			ObjectsOnDNA four = new ObjectsOnDNA("Nucleosome", "Binding", 20, 5);
			ObjectsOnDNA five = new ObjectsOnDNA("Transcriptional_Machinery", "Crick", 5, 5);
			InstructionObject IO8 = new InstructionObject(five, "CreateTranscriptionalMachinery");
			InstructionObject IO1 = new InstructionObject(one, "1,2,3");
			InstructionObject IO2 = new InstructionObject(two, "two");
			InstructionObject IO3 = new InstructionObject(three, "CreateTranscriptionFactor");
			InstructionObject IO4 = new InstructionObject(four, "CreateNucleosome");
			InstructionObject IO5 = new InstructionObject(four, "20, 0, 0");
			InstructionObject IO6 = new InstructionObject(three, "40, 0, 0");
			InstructionObject IO7 = new InstructionObject(five, "30, 0, 0");
			InstructionObject IO9 = new InstructionObject(five, "10, 0, 0");
			listIO.Add(IO8);
			listIO.Add(IO1);
			listIO.Add(IO2);
			listIO.Add(IO3);
			listIO.Add(IO4);
			listIO.Add(IO5);
			listIO.Add(IO6);
			listIO.Add(IO7);
			listIO.Add(IO9);
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
						//Extract coordinates and place into xyz array
						int[] xyz = new int[3];
						int index = 0;
						foreach(string j in current.instruction.Split(','))
						{
							xyz[index] = Convert.ToInt32(j);
							index++;
						}
						
						GameObject[] nucleosomes = GameObject.FindGameObjectsWithTag ("Nucleosome");
						GameObject[] transcriptionFactors = GameObject.FindGameObjectsWithTag("TranscriptionFactor");
						GameObject[] transcriptionalMachineries = GameObject.FindGameObjectsWithTag("TranscriptionalMachinery");
						
						float convertPos = (current.TranscriptionSimObject.StartPosition / 3.5f) - .6f;
						
						//Nucleosome move handling
						if(current.TranscriptionSimObject.MainType == "Nucleosome")
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
						if(current.TranscriptionSimObject.MainType == "Transcription_Factor")
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
						if(current.TranscriptionSimObject.MainType == "Transcriptional_Machinery")
						{
							Debug.Log("TM Start: " + convertPos);
							foreach(GameObject tm in transcriptionalMachineries)
							{
								Debug.Log("list of tms: " + tm.transform.position);
								if(convertPos == tm.transform.position.x)
								{
									Debug.Log("positions equal");
									iTween.MoveTo(tm, iTween.Hash("x", xyz[0], "time", 5));
									Debug.Log("new pos: " + tm.transform.position);
									current.TranscriptionSimObject.StartPosition = xyz[0];
									tm.transform.position = new Vector3(xyz[0] / 3.5f - .6f, 0, .3f);
									
								}
							}
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
