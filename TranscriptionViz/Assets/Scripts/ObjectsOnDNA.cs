using UnityEngine;
using System.Collections;
using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.Reflection;
using System.Linq;
#if UNITY_EDITOR
using UnityEditor;
#endif

public class ObjectsOnDNA
{
	public string MainType;
	public string Subtype;
	public float StartPosition;
	public float Length;

	public ObjectsOnDNA(string maintype, string subtype, float startPosition, float length)
	{
		MainType = maintype;
		Subtype = subtype;
		StartPosition = startPosition;
		Length = length;
	}

	public static void DeleteObject(ObjectsOnDNA toDelete)
	{
		GameObject[] nucleosomes = GameObject.FindGameObjectsWithTag ("Nucleosome");
		GameObject[] transcriptionFactors = GameObject.FindGameObjectsWithTag("TranscriptionFactor");
		GameObject[] transcriptionalMachineries = GameObject.FindGameObjectsWithTag("TranscriptionalMachinery");

		//toDelete.StartPosition has to be converted to nucleotide location
		float convertPos = (toDelete.StartPosition / 3.5f) - .6f;

		foreach (GameObject nuc in nucleosomes)
		{
			if (nuc.transform.position.x == convertPos)
			{

				GameObject.Destroy (nuc);
			}
		}

		foreach (GameObject tf in transcriptionFactors)
		{
			if (tf.transform.position.x == convertPos)
			{
				GameObject.Destroy (tf);
			}
		}


		foreach (GameObject tm in transcriptionalMachineries)
		{
			if (tm.transform.position.x == convertPos)
			{
				GameObject.Destroy (tm);
			}
		}


	}

}
