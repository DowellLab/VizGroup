﻿using UnityEngine;
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
				iTween.MoveTo (nuc, new Vector3 (10, -25, 0), 2f);
//				iTween.MoveTo (nuc, new Vector3 (convertPos, -20, -5), 0.1f);
			}

		}

		foreach (GameObject nuc in nucleosomes) 
		{
			if (nuc.transform.position.y == -25)
			{
				GameObject.Destroy (nuc);
			}
		}


		foreach (GameObject tf in transcriptionFactors)
		{
			if (tf.transform.position.x == convertPos)
			{
				iTween.MoveTo (tf, new Vector3 (convertPos, -20, -5), 2f);
			}
		}

		foreach (GameObject tf in transcriptionFactors) 
		{
			if (tf.transform.position.y == -20)
			{
				GameObject.Destroy (tf);
			}
		}




		foreach (GameObject tm in transcriptionalMachineries)
		{
			if (tm.transform.position.x == convertPos)
			{
				iTween.MoveTo (tm, new Vector3 (convertPos, -20, -5), 2f);
//				GameObject.Destroy (tm);
			}
		}

		foreach (GameObject tm in transcriptionalMachineries) 
		{
			if (tm.transform.position.y == -20)
			{
				GameObject.Destroy (tm);
			}
		}

	}

	public static void MoveObject(ObjectsOnDNA toMove, float xPosition) 
	{
		GameObject[] nucleosomes = GameObject.FindGameObjectsWithTag ("Nucleosome");
		GameObject[] transcriptionFactors = GameObject.FindGameObjectsWithTag("TranscriptionFactor");
		GameObject[] transcriptionalMachineries = GameObject.FindGameObjectsWithTag("TranscriptionalMachinery");

		//toDelete.StartPosition has to be converted to nucleotide location
		float convertPos = 0;
		float tempStartPos = 0;

		// Locate where to move to
		float tempMovePoint = 0;
		float finalMovePoint = 0;

		// SET LOCATIONS
		if (toMove.MainType == "'Nucleosome'")
		{
			// Locate Object to Move
			tempStartPos = toMove.StartPosition + (toMove.Length / 4);
			convertPos = (tempStartPos / 3.5f) - .6f;

			// Locate where to move to
			tempMovePoint = xPosition + (toMove.Length / 4);
			finalMovePoint = (tempMovePoint / 3.5f) - 0.6f;

		} else if (toMove.MainType == "'Transcription_Factor'"){

			tempStartPos = toMove.StartPosition + (toMove.Length / 3.5f);
			convertPos = (tempStartPos / 3.5f) - .6f;

			// Locate where to move to
			tempMovePoint = xPosition + (toMove.Length / 3.5f);
			finalMovePoint = (tempMovePoint / 3.5f) - 0.6f;

		} else if (toMove.MainType == "'Transcriptional_Machinery"){

			tempStartPos = toMove.StartPosition + (toMove.Length / 3.5f);
			convertPos = (tempStartPos / 3.5f) - .6f;

			// Locate where to move
			tempMovePoint = xPosition + (toMove.Length / 3.5f);
			finalMovePoint = (tempMovePoint / 3.5f) - 0.6f;
		}


		// HANDLE MOVEMENT
		foreach (GameObject nuc in nucleosomes)
		{
			if (nuc.transform.position.x == convertPos)
			{
				iTween.MoveTo (nuc, new Vector3 (finalMovePoint, 0.3f, 0), 2f);
			}
		}

		foreach (GameObject tf in transcriptionFactors)
		{
			if (tf.transform.position.x == convertPos)
			{
				iTween.MoveTo (tf, new Vector3 (finalMovePoint, 0.3f, 0), 2f);
			}
		}

		foreach (GameObject tm in transcriptionalMachineries)
		{
			if (tm.transform.position.x == convertPos)
			{
				iTween.MoveTo (tm, new Vector3 (finalMovePoint, 0.3f, 0), 2f);
			}
		}



	}

}
