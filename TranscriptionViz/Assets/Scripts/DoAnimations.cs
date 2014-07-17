using UnityEngine;
using System.Collections;
using System;
using System.Collections.Generic;

public class DoAnimations : MonoBehaviour
{

		List<ObjectsOnDNA> objs  = new List<ObjectsOnDNA>();
//		LinkedList<List<ObjectsOnDNA>> mylist = new LinkedList<List<ObjectsOnDNA>>();

		public IEnumerator createshit (ObjectsOnDNA obj)
		{
		
			yield return TranscriptionFactorClass.CreateTranscriptionFactor(obj);
			
		}
		//LinkedList<List<ObjectsOnDNA>> list
		void parseList ()
		{
			ObjectsOnDNA one = new ObjectsOnDNA("Transcription_Factor", "MCM1", 5, 5);
			ObjectsOnDNA two = new ObjectsOnDNA("Transcription_Factor", "REB1", 10, 5);
			ObjectsOnDNA three = new ObjectsOnDNA("Nucleosome", "Stable", 15, 5);
			ObjectsOnDNA four = new ObjectsOnDNA("Nucleosome", "Binding", 20, 5);
			objs.Add(one);
			objs.Add(two);
			objs.Add(three);
			objs.Add(four);
			foreach (ObjectsOnDNA thing in objs)
			{
				Debug.Log(thing.Subtype);
			}
		}

		// Use this for initialization
		void Start ()
		{
		
			
			String move = "10,20,30";
			
			int[] xyz = new int[3];
			int index = 0;
			foreach(string j in move.Split(','))
			{
				xyz[index] = Convert.ToInt32(j);
				index++;
				if(index >= 3)
				{
					index = 0;
				}
			}
			

			//ObjectsOnDNA TF  = new ObjectsOnDNA("Transcription_Factor", "REB1", 100, 5);
			//InstructionObject IO = new InstructionObject(TF, move);

			//iTween.MoveTo(chadobj, iTween.Hash("x", xyz[0], "y", xyz[1], "z", xyz[2], "time", 5));
			//IO.TranscriptionSimObject.transform.position += new Vector3(xyz[0], xyz[1], xyz[2]);

				
		}
	
		// Update is called once per frame
		void Update ()
		{
			if (Input.GetMouseButtonDown(0))
			{
				//StartCoroutine_Auto(createshit(TF));
			}
			
		}
		
}
