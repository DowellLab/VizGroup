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

		NewTranscriptionalMachinery.transform.position = new Vector3 ((TM.StartPosition / 3.5f) - 0.6f, 0.3f, 0);

		NewTranscriptionalMachinery.name = "TranscriptionalMachinery";
		NewTranscriptionalMachinery.tag = "TranscriptionalMachinery";


		// Transcription Factor Color
		if (TM.Subtype == "Init0" || TM.Subtype == "Init1")
		{
			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (0.957f, 0.643f, 0.376f);

		} else if (TM.Subtype == "Crick-Forwards" || TM.Subtype == "Crick-Backwards"){

			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (0.874f, 0.412f, 0.118f);

		} else {

			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (0.855f, 0.647f, 0.125f);
		}

		return NewTranscriptionalMachinery;
	}
}