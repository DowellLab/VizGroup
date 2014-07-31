using UnityEngine;
using System.Collections;
using System;
using System.Collections.Generic;

public class syncObj
{
	public GameObject gObj;
	public float coord;
	
	public syncObj (GameObject g, float c)
	{
		gObj = g;
		coord = c;
	}
}





public class DoAnimations : MonoBehaviour
{
		
		public List<syncObj> syncList = new List<syncObj>();		
		
		//List of Instruction Objects to be placed on LinkedListNode				
		public List<InstructionObject> listIO = new List<InstructionObject>();
		public List<InstructionObject> listIO2 = new List<InstructionObject>();	
		public List<InstructionObject> listIO3 = new List<InstructionObject>();	
		
		//Linked list of a list of instruction objects
		public LinkedList<List<InstructionObject>> ll = new LinkedList<List<InstructionObject>>();

		public IEnumerator parseList (LinkedList<List<InstructionObject>> ll)
		{
			LinkedListNode<List<InstructionObject>> cursor;
			cursor = ll.First;


			while(cursor != null)
			{

//			yield return StartCoroutine_Auto (TimeStep.instance.JustWait ());

			foreach(InstructionObject current in cursor.Value)
				{
					int x;
					bool isNumeric = int.TryParse(current.instruction, out x);
					Debug.Log("CHAAAAAAAAAAAAAAAAAAAD" + x);
					
					//Create TF
					if (current.instruction == "TranscriptionFactorClass.CreateTranscriptionFactor")
					{
						yield return TranscriptionFactorClass.CreateTranscriptionFactor(current.TranscriptionSimObject);
					}
					
					//Create Nucleosome
					if(current.instruction == "NucleosomeClass.CreateNucleosome")
					{
						yield return NucleosomeClass.CreateNucleosome(current.TranscriptionSimObject);
					}
					
					//Create TM
					if (current.instruction == "TranscriptionalMachineryClass.CreateTranscriptionalMachinery")
					{
						yield return TranscriptionalMachineryClass.CreateTranscriptionalMachinery(current.TranscriptionSimObject);
					}
					
					//Delete ObjectsOnDNA
					if(current.instruction == "ObjectsOnDNA.DeleteObject")
					{
						Debug.Log("Here " + current.TranscriptionSimObject.MainType);
						ObjectsOnDNA.DeleteObject(current.TranscriptionSimObject);
						yield return 0;
					}

					//Move Handling
					else if (isNumeric)
					{
					
						//Extract coordinates and place into xyz array
						
					
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
									Debug.Log("Nuc positions equal");
									
									syncList.Add(new syncObj(nuc, x));
									//iTween.MoveTo(nuc, iTween.Hash("x", x, "time", 5));
									
									current.TranscriptionSimObject.StartPosition = x;
									nuc.transform.position = new Vector3((x / 3.5f) - .6f, .3f, 0);
								}
								else{
									Debug.Log("Nucleosomes not equal");
									Debug.Log("ConvertPos = " + convertPos + " Current.start = " + current.TranscriptionSimObject.StartPosition + " Nuc.start = " + nuc.transform.position.x);
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
									Debug.Log("TF positions equal");
									
									syncList.Add(new syncObj(tf, x));
									//iTween.MoveTo(tf, iTween.Hash("x", xyz[0], "time", 5));
									
									current.TranscriptionSimObject.StartPosition = x;
									tf.transform.position = new Vector3((x / 3.5f) - .6f, .3f, 0);
								}
							}
						
						}
					
					//Transcriptional Machinery move handling
					if(current.TranscriptionSimObject.MainType == "Transcriptional_Machinery")
					{
						
						foreach(GameObject tm in transcriptionalMachineries)
						{
							if(convertPos == tm.transform.position.x)
							{
								Debug.Log("TM positions equal");
								
								syncList.Add(new syncObj(tm, x));
								
								//iTween.MoveTo(tm, iTween.Hash("x", convertPos, "time", 5));
								
								current.TranscriptionSimObject.StartPosition = x;
								tm.transform.position = new Vector3((x / 3.5f) - .6f, .3f, 0);				
							}
							else
							{
								Debug.Log("ConvertPos = " + convertPos + " Current.start = " + current.TranscriptionSimObject.StartPosition + " TM.start = " + tm.transform.position.x);
								
							}
						}
						
					}

					}	

				if (current.instruction == "JustWait")
				{
					Debug.Log("KNOWS TO WAIT");
					yield return TimeStep.instance.JustWait ();
					Debug.Log("TRIED TO WAIT");
				}
	
				foreach(syncObj s in syncList)
				{
					Debug.Log("obj shit" + s.gObj.name);
					iTween.MoveTo(s.gObj, iTween.Hash("x", s.coord, "time", 5));
					Debug.Log("Sync coords: " + s.coord);
				}

			}
				yield return new WaitForSeconds(6);
				syncList.Clear();
				cursor = cursor.Next;
			}
		}

		// Use this for initialization
		void Start ()
		{
		//Adding/Altering Linked List
		
//		ObjectsOnDNA one = new ObjectsOnDNA("Transcription_Factor", "MCM1", 5, 5);
//		ObjectsOnDNA two = new ObjectsOnDNA("Nucleosome", "Binding", 20, 5);
//		ObjectsOnDNA three = new ObjectsOnDNA("Transcriptional_Machinery", "Crick", 30, 5);
//		
//		InstructionObject IO1 = new InstructionObject(one, "TranscriptionFactorClass.CreateTranscriptionFactor");
//		InstructionObject IO2 = new InstructionObject(two, "NucleosomeClass.CreateNucleosome");
//		InstructionObject IO3 = new InstructionObject(three, "TranscriptionalMachineryClass.CreateTranscriptionalMachinery");
//		InstructionObject IO4 = new InstructionObject(one, "20");
//		InstructionObject IO5 = new InstructionObject(two, "40");	
//		InstructionObject IO6 = new InstructionObject(three, "10");
//		InstructionObject IO7 = new InstructionObject(three, "35");
//		InstructionObject IO8 = new InstructionObject(two, "2");
//		
//		listIO.Add(IO1);
//		listIO.Add(IO2);
//		listIO.Add(IO3);
//		
//		listIO2.Add(IO4);
//		listIO2.Add(IO5);
//		listIO2.Add(IO6);
//		
//		listIO3.Add(IO7);
//		listIO3.Add(IO8);
//		
//		
//		ll.AddFirst(listIO);
//		ll.AddLast(listIO2);
//		ll.AddLast(listIO3);
			
		}
					
		

		// Update is called once per frame
		void Update ()
		{
		
		//execute when space is pressed
		if (Input.GetKeyDown("space")) {
			
			StartCoroutine(parseList(ll));
		}	


		}
		
}
