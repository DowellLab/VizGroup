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
		float convertPos = 0;
		float tempStartPos = 0;

		if (toDelete.MainType == "'Nucleosome'")
		{
			tempStartPos = toDelete.StartPosition + (toDelete.Length / 4);
			convertPos = (tempStartPos / 3.5f) - .6f;

		} else if (toDelete.MainType == "'Transcription_Factor'"){

			tempStartPos = toDelete.StartPosition + (toDelete.Length / 3.5f);
			convertPos = (tempStartPos / 3.5f) - .6f;

		} else if (toDelete.MainType == "'Transcriptional_Machinery"){

			tempStartPos = toDelete.StartPosition + (toDelete.Length / 3.5f);
			convertPos = (tempStartPos / 3.5f) - .6f;
		}


		foreach (GameObject nuc in nucleosomes)
		{
			if (nuc.transform.position.x == convertPos)
			{
				iTween.MoveTo (nuc, new Vector3 (10, -25, 0), 1.5f);
//				iTween.MoveTo (nuc, new Vector3 (convertPos, -20, -5), 0.1f);
				GameObject.Destroy (nuc);
			}
		}

		foreach (GameObject tf in transcriptionFactors)
		{
			if (tf.transform.position.x == convertPos)
			{
				iTween.MoveTo (tf, new Vector3 (convertPos, -20, -5), 1f);
				GameObject.Destroy (tf);
			}
		}


		foreach (GameObject tm in transcriptionalMachineries)
		{
			if (tm.transform.position.x == convertPos)
			{
				iTween.MoveTo (tm, new Vector3 (convertPos, -20, -5), 1f);
				GameObject.Destroy (tm);
			}
		}


	}

}
