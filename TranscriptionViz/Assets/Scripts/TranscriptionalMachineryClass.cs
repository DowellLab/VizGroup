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

public class TranscriptionalMachineryClass
{
	//	static int speed = 300;

	public string Subtype;
	public float StartPosition;
	public float Length;

	public TranscriptionalMachineryClass(string subtype, float startPosition, float length)
	{
		Subtype = subtype;
		StartPosition = startPosition;
		Length = length;

	}

	public static GameObject CreateTranscriptionalMachinery(string Subtype, float StartPosition, float Length)
	{
		GameObject NewTranscriptionalMachinery;
		NewTranscriptionalMachinery = GameObject.CreatePrimitive (PrimitiveType.Cylinder);
		NewTranscriptionalMachinery.transform.localScale = new Vector3 (Length / 3.5f, Length / 5, Length / 5);		// Scale extends on both sides, so is a bad ultimate choice
		NewTranscriptionalMachinery.renderer.material.shader = Shader.Find("Specular");

		StartPosition += Length / 3.5f;

		NewTranscriptionalMachinery.transform.position = new Vector3 ((StartPosition / 3.5f) - 0.6f, 0.3f, 0);

		NewTranscriptionalMachinery.name = "TranscriptionalMachinery";
		NewTranscriptionalMachinery.tag = "TranscriptionalMachinery";


		// Transcription Factor Color
		if (Subtype == "Init0" || Subtype == "Init1")
		{
			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (0.957f, 0.643f, 0.376f);

		} else if (Subtype == "Crick-Forwards" || Subtype == "Crick-Backwards"){

			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (0.874f, 0.412f, 0.118f);

		} else {

			NewTranscriptionalMachinery.gameObject.renderer.material.color = new Color (0.855f, 0.647f, 0.125f);
		}

		return NewTranscriptionalMachinery;
	}
}