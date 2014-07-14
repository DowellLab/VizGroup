using UnityEngine;
using System.Collections;
using System;

public class Animator : MonoBehaviour
{

		// Use this for initialization
		void Start ()
		{
			GameObject nucleosome  = new GameObject();
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

		
			InstructionObject IO = new InstructionObject(nucleosome, move);
			IO.TranscriptionSimObject = GameObject.CreatePrimitive(PrimitiveType.Sphere);
			
			iTween.MoveTo(IO.TranscriptionSimObject, iTween.Hash("x", xyz[0], "y", xyz[1], "z", xyz[2], "time", 5));
			//IO.TranscriptionSimObject.transform.position += new Vector3(xyz[0], xyz[1], xyz[2]);

				
		}
	
		// Update is called once per frame
		void Update ()
		{
	
		}
}
