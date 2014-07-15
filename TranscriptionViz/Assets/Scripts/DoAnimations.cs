using UnityEngine;
using System.Collections;
using System;

public class DoAnimations : MonoBehaviour
{

		ObjectsOnDNA TF  = new ObjectsOnDNA("Transcription_Factor", "REB1", 100, 5);

		public IEnumerator createshit (ObjectsOnDNA obj)
		{
		
			yield return TranscriptionFactorClass.CreateTranscriptionFactor(obj);
			
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
				StartCoroutine_Auto(createshit(TF));
			}
			
		}
		
}
