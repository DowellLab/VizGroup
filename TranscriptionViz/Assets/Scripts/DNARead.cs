using System;
using System.IO;
using UnityEngine;
using System.Collections.Generic;

public class DNARead : MonoBehaviour 
{

	public GameObject Tprefab;
	public GameObject Aprefab;
	public GameObject Cprefab;
	public GameObject Gprefab;
	public GameObject Hprefab;

	//Allows me to keep track of all helixes so that the positions
	//of nucleotides can be computed accordingly.
	public List <GameObject> helixList;


	private GameObject hel;
	private string text;
	private int strnlength;
	private int i;

	// Where the start of the sequence is going to be located?
	private int helixPositionOffset;										

	Vector3 Compute_DNA_Position(int position)
	{
			Vector3 helixOrigin = helixList [(int)Math.Ceiling (position / 7.0) - 1].transform.position;

			return new Vector3(helixOrigin.x + (-0.9f + (i%7) * 0.3f), helixOrigin.y, helixOrigin.z);
	}

	void Get_Compilmentary_Nucleotide(char c, GameObject helix)
	{
		if (c == 'A') 
		{
			GameObject thymine = (GameObject) Instantiate(Tprefab, helix.transform.position, Quaternion.AngleAxis(90, Vector3.right));
			thymine.transform.Rotate(new Vector3(180,90,0), Space.World);
			thymine.transform.parent = helix.transform;
			thymine.transform.Translate(-0.9f+(i%7)*0.3f, 0.420f, 0.0f, Space.World);
		}

		if (c == 'T') 
		{
			GameObject adenine = (GameObject) Instantiate(Aprefab, helix.transform.position, Quaternion.AngleAxis(90, Vector3.right));
			adenine.transform.Rotate(new Vector3(0,90,0), Space.World);
			adenine.transform.parent = helix.transform;
			adenine.transform.Translate(-0.9f+(i%7)*0.3f, 0.420f, 0.0f, Space.World);
		}

		if (c == 'G') 
		{
			GameObject cytosine = (GameObject) Instantiate(Cprefab, helix.transform.position, Quaternion.AngleAxis(90, Vector3.right));
			cytosine.transform.Rotate(new Vector3(180,90,0), Space.World);
			cytosine.transform.parent = helix.transform;
			cytosine.transform.Translate(-0.9f+(i%7)*0.3f, 0.46f, 0.0f, Space.World);
		}

		if (c == 'C') 
		{
			GameObject guanine = (GameObject) Instantiate(Gprefab, helix.transform.position, Quaternion.AngleAxis(90, Vector3.right));
			guanine.transform.Rotate(new Vector3(180,90,0), Space.World);
			guanine.transform.parent = helix.transform;
			guanine.transform.Translate(-0.9f+(i%7)*0.3f, 0.46f, 0.0f, Space.World);
		}

	}

	// Use this for initialization
	void Start () 
	{
			//Iterator to keep track of where we are in the string.
			i = 0;

			//Read the whole file into one string
			text = File.ReadAllText("DNAtest.txt");
			strnlength = text.Length;



			// Initialize list to hold helix peices
			helixList = new List <GameObject> ();

	}
	
	
	// Update is called once per frame
	void Update () 
	{
			// based on letter (nucleotide) found, different shapes are placed in a line starting and
			// increment by 3. A new shape is added each frame.
			if (i < strnlength) 
			{

				if(i % 7 == 0)
				{
					hel = (GameObject) Instantiate(Hprefab, new Vector3((i/7 * 2), 0, 0), Quaternion.AngleAxis(90, Vector3.up));
					helixList.Add (hel);
				}

				switch(text[i])
				{
					//Insantiates nucleotides and places as children to respective helix and transforms accordingly.
					case 'A':
						GameObject adenine = (GameObject) Instantiate(Aprefab, hel.transform.position, Quaternion.AngleAxis(90, Vector3.right));
						adenine.transform.Rotate(new Vector3(180,90,0), Space.World);
						adenine.transform.parent = hel.transform;
						adenine.transform.Translate(-0.9f+(i%7)*0.3f, 0.15f, 0.0f, Space.World);
						//GameObject go = Instantiate(Resources.Load("MyPrefab")) as GameObject; 

						Get_Compilmentary_Nucleotide('A', hel);
						break;
						
					case 'T':
						GameObject thymine = (GameObject) Instantiate(Tprefab, hel.transform.position, Quaternion.AngleAxis(90, Vector3.right));
						thymine.transform.Rotate(new Vector3(0,90,0), Space.World);
						thymine.transform.parent = hel.transform;
						thymine.transform.Translate(-0.9f+(i%7)*0.3f, 0.15f, 0.0f, Space.World);

						Get_Compilmentary_Nucleotide('T', hel);
						break;
						
					case 'G':
						GameObject guanine = (GameObject) Instantiate(Gprefab, hel.transform.position, Quaternion.AngleAxis(90, Vector3.right));
						guanine.transform.Rotate(new Vector3(0,90,0), Space.World);
						guanine.transform.parent = hel.transform;
						guanine.transform.Translate(-0.9f+(i%7)*0.3f, 0.15f, 0.0f, Space.World);

						Get_Compilmentary_Nucleotide('G', hel);
						break;
						
					case 'C':
						GameObject cytosine = (GameObject) Instantiate(Cprefab, hel.transform.position, Quaternion.AngleAxis(90, Vector3.right));
						cytosine.transform.Rotate(new Vector3(0,90,0), Space.World);
						cytosine.transform.parent = hel.transform;
						cytosine.transform.Translate(-0.9f+(i%7)*0.3f, 0.15f, 0.0f, Space.World);
						
						Get_Compilmentary_Nucleotide('C', hel);
						break; 
				}

			//Flips helix
			//Significant nucleotides are now on top.
			//hel.transform.Rotate(new Vector3(180,0,0), Space.World);

			++i;

		}

		if(Input.GetKeyDown(KeyCode.D))
		{
			GameObject capsule = GameObject.CreatePrimitive(PrimitiveType.Capsule);
			capsule.transform.position = Compute_DNA_Position(20);
		}

	}



}

