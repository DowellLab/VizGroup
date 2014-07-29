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

public class TranscriptionFactorClass : ObjectsOnDNA
{
	public static Shader specular = Shader.Find("Specular");

	public TranscriptionFactorClass(string maintype, string subtype, float startPosition, float length) : base(maintype, subtype, startPosition, length)
	{
		MainType = maintype;
		Subtype = subtype;
		StartPosition = startPosition;
		Length = length;

	}

	public static GameObject CreateTranscriptionFactor(ObjectsOnDNA TF)
	{

		

		// Transcription Factor Color
		if (TF.Subtype == "'REB1'")
		{
			GameObject NewTranscriptionFactor = GameObject.CreatePrimitive (PrimitiveType.Cube);
			NewTranscriptionFactor.transform.localScale = new Vector3 (TF.Length / 3.5f, TF.Length / 3.5f, TF.Length / 3.5f);		// Scale extends on both sides, so is a bad ultimate choice
			NewTranscriptionFactor.renderer.material.shader = specular;
			
			TF.StartPosition += TF.Length / 3.5f;
			
			//		NewTranscriptionFactor.transform.position = new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0);
			
			NewTranscriptionFactor.transform.position = new Vector3 (15, 25, 0);
			iTween.MoveTo (NewTranscriptionFactor, new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0), 1.5f);
			
			NewTranscriptionFactor.name = "TranscriptionFactor";
			NewTranscriptionFactor.tag = "TranscriptionFactor";
			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (1, 0, 1);
			return NewTranscriptionFactor;

		} else if (TF.Subtype == "'TBP'") {

			GameObject NewTranscriptionFactor = GameObject.CreatePrimitive (PrimitiveType.Cube);
			NewTranscriptionFactor.transform.localScale = new Vector3 (TF.Length / 3.5f, TF.Length / 3.5f, TF.Length / 3.5f);		// Scale extends on both sides, so is a bad ultimate choice
			NewTranscriptionFactor.renderer.material.shader = specular;
			
			TF.StartPosition += TF.Length / 3.5f;
			
			//		NewTranscriptionFactor.transform.position = new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0);
			
			NewTranscriptionFactor.transform.position = new Vector3 (15, 25, 0);
			iTween.MoveTo (NewTranscriptionFactor, new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0), 1.5f);
			
			NewTranscriptionFactor.name = "TranscriptionFactor";
			NewTranscriptionFactor.tag = "TranscriptionFactor";
			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0.6f, 1, 0.3f);
			return NewTranscriptionFactor;

		} else if (TF.Subtype == "'MCM1'"){

			GameObject NewTranscriptionFactor = GameObject.CreatePrimitive (PrimitiveType.Cube);
			NewTranscriptionFactor.transform.localScale = new Vector3 (TF.Length / 3.5f, TF.Length / 3.5f, TF.Length / 3.5f);		// Scale extends on both sides, so is a bad ultimate choice
			NewTranscriptionFactor.renderer.material.shader = specular;
			
			TF.StartPosition += TF.Length / 3.5f;
			
			//		NewTranscriptionFactor.transform.position = new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0);
			
			NewTranscriptionFactor.transform.position = new Vector3 (15, 25, 0);
			iTween.MoveTo (NewTranscriptionFactor, new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0), 1.5f);
			
			NewTranscriptionFactor.name = "TranscriptionFactor";
			NewTranscriptionFactor.tag = "TranscriptionFactor";
			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0.729f, 0.333f, 0.827f);
			return NewTranscriptionFactor;

		} else if (TF.Subtype == "'DAL80'"){

			
			GameObject NewTranscriptionFactor = (GameObject) GameObject.Instantiate((Resources.Load<GameObject>("DAL80")));
			NewTranscriptionFactor.transform.localScale = new Vector3 (TF.Length / 100f, TF.Length / 100f, TF.Length / 100f);		// Scale extends on both sides, so is a bad ultimate choice

			
			TF.StartPosition += TF.Length / 3.5f;
			
			NewTranscriptionFactor.transform.position = new Vector3 (15, 25, 0);
			iTween.MoveTo (NewTranscriptionFactor, new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0), 1.5f);
			NewTranscriptionFactor.name = "TranscriptionFactor";
			NewTranscriptionFactor.tag = "TranscriptionFactor";
			
//			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0, 0, 0.831f);
			return NewTranscriptionFactor;
			
		} else if (TF.Subtype == "'FLO8'"){
			
			
			GameObject NewTranscriptionFactor = (GameObject) GameObject.Instantiate((Resources.Load<GameObject>("FLO8")));
			NewTranscriptionFactor.transform.localScale = new Vector3 (TF.Length / 100f, TF.Length / 100f, TF.Length / 100f);		// Scale extends on both sides, so is a bad ultimate choice
			
			
			TF.StartPosition += TF.Length / 3.5f;
			
			NewTranscriptionFactor.transform.position = new Vector3 (15, 25, 0);
			iTween.MoveTo (NewTranscriptionFactor, new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0), 1.5f);
			NewTranscriptionFactor.name = "TranscriptionFactor";
			NewTranscriptionFactor.tag = "TranscriptionFactor";
			
			//			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0, 0, 0.831f);
			return NewTranscriptionFactor;

		} else {


			GameObject NewTranscriptionFactor = GameObject.CreatePrimitive (PrimitiveType.Cube);
			NewTranscriptionFactor.transform.localScale = new Vector3 (TF.Length / 3.5f, TF.Length / 3.5f, TF.Length / 3.5f);		// Scale extends on both sides, so is a bad ultimate choice
			NewTranscriptionFactor.renderer.material.shader = specular;
			
			TF.StartPosition += TF.Length / 3.5f;
			
			//		NewTranscriptionFactor.transform.position = new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0);
			
			NewTranscriptionFactor.transform.position = new Vector3 (15, 25, 0);
			iTween.MoveTo (NewTranscriptionFactor, new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0), 1.5f);
			
			NewTranscriptionFactor.name = "TranscriptionFactor";
			NewTranscriptionFactor.tag = "TranscriptionFactor";
			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0, 0.85f, 0);
			return NewTranscriptionFactor;
		}


		//		iTween.MoveTo (NewTranscriptionFactor, new Vector3 ((StartPosition/3), 0, 0), 2);

	}

}