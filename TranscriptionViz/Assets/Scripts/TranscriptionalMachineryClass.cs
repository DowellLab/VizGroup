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

public class TranscriptionalMachineryClass : ObjectsOnDNA
{
	public static Shader specular = Shader.Find("Specular");

	public TranscriptionalMachineryClass(string maintype, string subtype, float startPosition, float length) : base(maintype, subtype, startPosition, length)
	{
		MainType = maintype;
		Subtype = subtype;
		StartPosition = startPosition;
		Length = length;

	}

	public static GameObject CreateTranscriptionalMachinery(ObjectsOnDNA TM)
	{
		GameObject NewTranscriptionalMachinery;
		NewTranscriptionalMachinery = GameObject.CreatePrimitive (PrimitiveType.Cylinder);
		NewTranscriptionalMachinery.transform.localScale = new Vector3 (TM.Length / 3.5f, TM.Length / 5, TM.Length / 5);		// Scale extends on both sides, so is a bad ultimate choice
		NewTranscriptionalMachinery.renderer.material.shader = Shader.Find("Specular");

		TM.StartPosition += TM.Length / 3.5f;

//		NewTranscriptionalMachinery.transform.position = new Vector3 ((TM.StartPosition / 3.5f) - 0.6f, 0.3f, 0);

		NewTranscriptionalMachinery.transform.position = new Vector3 (10, 25, 0);
		iTween.MoveTo (NewTranscriptionalMachinery, new Vector3 ((TM.StartPosition / 3.5f) - 0.6f, 0.3f, 0), 1.5f);



		NewTranscriptionalMachinery.name = "TranscriptionalMachinery";
		NewTranscriptionalMachinery.tag = "TranscriptionalMachinery";


		// Transcription Factor Color
		if (TM.Subtype == "'Crick-Init0'" || TM.Subtype == "'Crick-Init1'" || TM.Subtype == "'Crick-Init2'" || TM.Subtype == "'Crick-Init3'" || TM.Subtype == "'Crick-Init4'") {
			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (0.957f, 0.643f, 0.376f);

		} else if (TM.Subtype == "'Watson-Init0'" || TM.Subtype == "'Watson-Init1'" || TM.Subtype == "'Watson-Init2'" || TM.Subtype == "'Watson-Init3'" || TM.Subtype == "'Watson-Init4'") {

			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (0.957f, 0.643f, 0.376f);

		} else if (TM.Subtype == "'Crick'" || TM.Subtype == "'Watson'") {

			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (0.874f, 0.412f, 0.118f);

		} else if (TM.Subtype == "'Crick-Transcribed'" || TM.Subtype == "'Watson-Transcribed'") {

			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (0.800f, 0.500f, 0.118f);

		} else if (TM.Subtype == "'Crick-Paused'" || TM.Subtype == "'Watson-Paused'") {

			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (0.874f, 0.412f, 0.118f);

		} else {

			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (0.855f, 0.647f, 0.125f);
		}

		return NewTranscriptionalMachinery;
	}

	public static void ChangeTM(ObjectsOnDNA toChange, string newSub, float convertPos )
	{
		GameObject[] transcriptionalMachineries = GameObject.FindGameObjectsWithTag("TranscriptionalMachinery");

		foreach (GameObject tm in transcriptionalMachineries)
		{
			if (tm.transform.position.x == convertPos)
			{
				if (newSub == "'Crick-Init0'" || newSub == "'Crick-Init1'" || newSub == "'Crick-Init2'" || newSub == "'Crick-Init3'" || newSub == "'Crick-Init4'") {
					tm.gameObject.renderer.material.color = new Color (0.957f, 0.643f, 0.376f);

				} else if (newSub == "'Watson-Init0'" || newSub == "'Watson-Init1'" || newSub == "'Watson-Init2'" || newSub == "'Watson-Init3'" || newSub == "'Watson-Init4'") {

					tm.gameObject.renderer.material.color = new Color (0.957f, 0.643f, 0.376f);

				} else if (newSub == "'Crick'" || newSub == "'Watson'") {

					tm.gameObject.renderer.material.color = new Color (0.874f, 0.412f, 0.118f);

				} else if (newSub == "'Crick-Transcribed'" || newSub == "'Watson-Transcribed'") {

					tm.gameObject.renderer.material.color = new Color (0.800f, 0.500f, 0.118f);

				} else if (newSub == "'Crick-Paused'" || newSub == "'Watson-Paused'") {

					tm.gameObject.renderer.material.color = new Color (0.874f, 0.412f, 0.118f);

				} else {

					tm.gameObject.renderer.material.color = new Color (0.855f, 0.647f, 0.125f);
				}
			}

		}

	}

}