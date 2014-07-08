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

public class TranscriptionFactorClass
{

	public string Subtype;
	public float StartPosition;
	public float Length;
	public static Shader specular = Shader.Find("Specular");

	public TranscriptionFactorClass(string subtype, float startPosition, float length)
	{
		Subtype = subtype;
		StartPosition = startPosition;
		Length = length;

	}

	public static GameObject CreateTranscriptionFactor(string Subtype, float StartPosition, float Length)
	{
		GameObject NewTranscriptionFactor;
		NewTranscriptionFactor = GameObject.CreatePrimitive (PrimitiveType.Cube);
		NewTranscriptionFactor.transform.localScale = new Vector3 (Length / 3.5f, Length / 3.5f, Length / 3.5f);		// Scale extends on both sides, so is a bad ultimate choice
		NewTranscriptionFactor.renderer.material.shader = specular;

		StartPosition += Length / 3.5f;

		NewTranscriptionFactor.transform.position = new Vector3 ((StartPosition / 3.5f) - 0.6f, 0.3f, 0);

		//		NewTranscriptionFactor.transform.position = new Vector3 (15, -25, 0);

		NewTranscriptionFactor.name = "TranscriptionFactor";
		NewTranscriptionFactor.tag = "TranscriptionFactor";


		// Transcription Factor Color
		if (Subtype == "REB1")
		{
			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (1, 0, 1);

		} else if (Subtype == "TBP") {

			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0.6f, 1, 0.3f);

		} else if (Subtype == "MCM1"){

			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0.729f, 0.333f, 0.827f);

		} else if (Subtype == "DAL80"){

			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0, 0, 0.831f);

		} else {

			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0, 0.85f, 0);
		}


		//		iTween.MoveTo (NewTranscriptionFactor, new Vector3 ((StartPosition/3), 0, 0), 2);



		return NewTranscriptionFactor;
	}

}