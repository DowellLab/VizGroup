using UnityEngine;
using System.Collections;

public class Animation : MonoBehaviour
{



		// Use this for initialization
		void Start ()
		{
				string chad = "create 4";
				string create = "create"; 
				if(chad.StartsWith(create))
				{
					Debug.Log (chad);
				}
				else
				{
					Debug.Log("no create");
				}
				
		}
	
		// Update is called once per frame
		void Update ()
		{
	
		}
}
