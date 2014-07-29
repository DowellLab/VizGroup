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
<<<<<<< HEAD
=======
		GameObject[] transcriptionFactors = GameObject.FindGameObjectsWithTag("TranscriptionFactor");

		GameObject NewTranscriptionFactor;

		var proceedWithCreation = true;


		var tempStartPos = TF.StartPosition + (TF.Length / 3.5f);
		var convertPos = (tempStartPos / 3.5f) - .6f;

		foreach (GameObject tFactor in transcriptionFactors)
		{
			if (tFactor.transform.position.x == convertPos && tFactor.transform.position.y == 12.5f)
			{
				iTween.MoveTo (tFactor, new Vector3 (convertPos, 0.3f, 0), 2f);
				proceedWithCreation = false;
			}

		}

>>>>>>> origin/master

		

		if (proceedWithCreation == true)
		{
<<<<<<< HEAD
			GameObject NewTranscriptionFactor = GameObject.CreatePrimitive (PrimitiveType.Cube);
			NewTranscriptionFactor.transform.localScale = new Vector3 (TF.Length / 3.5f, TF.Length / 3.5f, TF.Length / 3.5f);		// Scale extends on both sides, so is a bad ultimate choice
			NewTranscriptionFactor.renderer.material.shader = specular;
			
			TF.StartPosition += TF.Length / 3.5f;
=======

			NewTranscriptionFactor = GameObject.CreatePrimitive (PrimitiveType.Cube);
			NewTranscriptionFactor.transform.localScale = new Vector3 (TF.Length / 3.5f, TF.Length / 3.5f, TF.Length / 3.5f);		// Scale extends on both sides, so is a bad ultimate choice
			NewTranscriptionFactor.renderer.material.shader = specular;

//			Debug.Log("REB1 CREATED!");
//			NewTranscriptionFactor = Resources.Load<GameObject>("TFModels/REB1");
>>>>>>> origin/master
			
			//		NewTranscriptionFactor.transform.position = new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0);
			
			NewTranscriptionFactor.transform.position = new Vector3 (15, 25, 0);
			iTween.MoveTo (NewTranscriptionFactor, new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0), 1.5f);
			
			NewTranscriptionFactor.name = "TranscriptionFactor";
			NewTranscriptionFactor.tag = "TranscriptionFactor";
			NewTranscriptionFactor.gameObject.renderer.material.color = new Color (1, 0, 1);
			return NewTranscriptionFactor;


<<<<<<< HEAD
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
=======
			TF.StartPosition += TF.Length / 3.5f;
>>>>>>> origin/master

			//		NewTranscriptionFactor.transform.position = new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0);

<<<<<<< HEAD
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
=======
			NewTranscriptionFactor.transform.position = new Vector3 (15, 25, 0);
			iTween.MoveTo (NewTranscriptionFactor, new Vector3 ((TF.StartPosition / 3.5f) - 0.6f, 0.3f, 0), 1.5f);
>>>>>>> origin/master

			NewTranscriptionFactor.name = "TranscriptionFactor";
			NewTranscriptionFactor.tag = "TranscriptionFactor";

<<<<<<< HEAD
			
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
=======
>>>>>>> origin/master


<<<<<<< HEAD

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
=======
			// Transcription Factor Color
			if (TF.Subtype == "'REB1'")
			{
				NewTranscriptionFactor.gameObject.renderer.material.color = new Color (1, 0, 1);

//				NewTranscriptionFactor = Resources.Load<GameObject>("TFModels/REB1");
>>>>>>> origin/master


			} else if (TF.Subtype == "'TBP'") {

<<<<<<< HEAD
=======
				NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0.6f, 1, 0.3f);

			} else if (TF.Subtype == "'MCM1'"){

				NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0.729f, 0.333f, 0.827f);

			} else if (TF.Subtype == "'DAL80'"){

				NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0, 0, 0.831f);

			} else {

				NewTranscriptionFactor.gameObject.renderer.material.color = new Color (0, 0.85f, 0);
			}

			return NewTranscriptionFactor;
		} else {

			return NewTranscriptionFactor = GameObject.FindGameObjectWithTag("TranscriptionFactor");
		}

>>>>>>> origin/master
	}

}