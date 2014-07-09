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
	// Offset for each nucleotide so that they have even spacing
	private float nucleotideOffset = 0.25f;

	Vector3 Compute_DNA_Position(int position)
	{
			Vector3 helixOrigin = helixList [(int)Math.Ceiling (position / 7.0) - 1].transform.position;

			return new Vector3(helixOrigin.x + (-0.9f + (i%7) * 0.3f), helixOrigin.y, helixOrigin.z);
	}

	void Get_Compilmentary_Nucleotide(char c, GameObject helix, int m)
	{
		if (c == 'A') 
		{
			GameObject thymine = (GameObject) Instantiate(Tprefab, helix.transform.position, Quaternion.AngleAxis(90, Vector3.right));
			thymine.transform.Rotate(new Vector3(180,90,0), Space.World);
			thymine.transform.parent = helix.transform;
			thymine.transform.Translate(-0.9f+(m%7)* nucleotideOffset, 0.420f, 0.0f, Space.World);
		}

		if (c == 'T') 
		{
			GameObject adenine = (GameObject) Instantiate(Aprefab, helix.transform.position, Quaternion.AngleAxis(90, Vector3.right));
			adenine.transform.Rotate(new Vector3(0,90,0), Space.World);
			adenine.transform.parent = helix.transform;
			adenine.transform.Translate(-0.9f+(m%7)* nucleotideOffset, 0.420f, 0.0f, Space.World);
		}

		if (c == 'G') 
		{
			GameObject cytosine = (GameObject) Instantiate(Cprefab, helix.transform.position, Quaternion.AngleAxis(90, Vector3.right));
			cytosine.transform.Rotate(new Vector3(180,90,0), Space.World);
			cytosine.transform.parent = helix.transform;
			cytosine.transform.Translate(-0.9f+(m%7)* nucleotideOffset, 0.46f, 0.0f, Space.World);
		}

		if (c == 'C') 
		{
			GameObject guanine = (GameObject) Instantiate(Gprefab, helix.transform.position, Quaternion.AngleAxis(90, Vector3.right));
			guanine.transform.Rotate(new Vector3(180,90,0), Space.World);
			guanine.transform.parent = helix.transform;
			guanine.transform.Translate(-0.9f+(m%7)* nucleotideOffset, 0.46f, 0.0f, Space.World);
		}

	}

	void Get_Significant_Nucleotide(char c, GameObject helix, int m)
	{
		switch(c)
		{
				//Insantiates nucleotides and places as children to respective helix and transforms accordingly.
			case 'A':
				GameObject adenine = (GameObject) Instantiate(Aprefab, helix.transform.position, Quaternion.AngleAxis(90, Vector3.right));
				adenine.transform.Rotate(new Vector3(180,90,0), Space.World);
				adenine.transform.parent = helix.transform;
				adenine.transform.Translate(-0.9f+(m%7)* nucleotideOffset, 0.15f, 0.0f, Space.World);
				//GameObject go = Instantiate(Resources.Load("MyPrefab")) as GameObject; 
				
				Get_Compilmentary_Nucleotide('A', hel, m);
				break;
				
			case 'T':
				GameObject thymine = (GameObject) Instantiate(Tprefab, helix.transform.position, Quaternion.AngleAxis(90, Vector3.right));
				thymine.transform.Rotate(new Vector3(0,90,0), Space.World);
				thymine.transform.parent = helix.transform;
				thymine.transform.Translate(-0.9f+(m%7)* nucleotideOffset, 0.15f, 0.0f, Space.World);
				
				Get_Compilmentary_Nucleotide('T', hel, m);
				break;
				
			case 'G':
				GameObject guanine = (GameObject) Instantiate(Gprefab, helix.transform.position, Quaternion.AngleAxis(90, Vector3.right));
				guanine.transform.Rotate(new Vector3(0,90,0), Space.World);
				guanine.transform.parent = helix.transform;
				guanine.transform.Translate(-0.9f+(m%7)* nucleotideOffset, 0.15f, 0.0f, Space.World);
				
				Get_Compilmentary_Nucleotide('G', hel, m);
				break;
				
			case 'C':
				GameObject cytosine = (GameObject) Instantiate(Cprefab, helix.transform.position, Quaternion.AngleAxis(90, Vector3.right));
				cytosine.transform.Rotate(new Vector3(0,90,0), Space.World);
				cytosine.transform.parent = helix.transform;
				cytosine.transform.Translate(-0.9f+(m%7)* nucleotideOffset, 0.15f, 0.0f, Space.World);
				
				Get_Compilmentary_Nucleotide('C', hel, m);
				break; 
		}

	}

	// Use this for initialization
	void Start () 
	{
				//Iterator to keep track of where we are in the string.
				i = 0;

				//Read the whole file into one string
				text = File.ReadAllText ("DNAtest.txt");
				strnlength = text.Length;


				// Initialize list to hold helix peices
				helixList = new List <GameObject> ();

				// based on letter (nucleotide) found, different shapes are placed in a line starting and
				// increment by 3. A new shape is added each frame.
				while (i < strnlength) 
				{
						// The position of the DNA is based on the positions of the helix pieces
						if (i % 7 == 0) 
						{
							hel = (GameObject)Instantiate (Hprefab, new Vector3 ((i / 7 * 2), 0, 0), Quaternion.AngleAxis (90, Vector3.up));
							helixList.Add (hel);
						}

						// Given the read nucleotide type, correct helix piece and nucleotide number the nucleotides are put into place.
						Get_Significant_Nucleotide (text[i], hel, i); 
						++i;
				}

				if (strnlength%7 != 0) 
				{
					for (int k = i; k < i + strnlength%7; ++k) 
					{
						Get_Significant_Nucleotide ('A', hel, k);
					}
				}
		}
	
	
	// Update is called once per frame
	void Update () 
	{

	}



}

