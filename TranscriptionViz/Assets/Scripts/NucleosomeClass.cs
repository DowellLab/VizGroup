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

public class NucleosomeClass
{
	public string Subtype;
	public float StartPosition;
	public float Length;

	public static Shader specular = Shader.Find("Specular");

	public NucleosomeClass(string subtype, float startPosition, float length)
	{
		Subtype = subtype;
		StartPosition = startPosition;
		Length = length;

	}


	public static GameObject CreateNucleosome(string Subtype, float StartPosition, float Length)
	{

		GameObject NewNucleosome;

		NewNucleosome = GameObject.CreatePrimitive (PrimitiveType.Sphere);

		if (StartPosition != 0) {
			NewNucleosome.transform.localScale = new Vector3 (Length / 3.5f, Length / 6f, Length / 3.5f); // Scale extends on both sides, so is a bad ultimate choice
		} else {
			NewNucleosome.transform.localScale = new Vector3 (Length / 3.5f, Length / 3f, Length / 3.5f);
		}

		NewNucleosome.renderer.material.shader = specular;

		StartPosition += Length / 4;
		NewNucleosome.transform.position = new Vector3 ((StartPosition / 3.5f) - 0.6f, 0.3f, 0);

		//		NewNucleosome.transform.position = new Vector3 (10, -25, 0);

		NewNucleosome.name = "Nucleosome";
		NewNucleosome.tag = "Nucleosome";

		// Nucleosome Color
		if (Subtype == "Binding")
		{
			NewNucleosome.gameObject.renderer.material.color = new Color (0.2f, 0.4f, 0.5f);

		} else if (Subtype == "Unbinding") {

			NewNucleosome.gameObject.renderer.material.color = new Color (0, 1, 1);

		} else {

			NewNucleosome.gameObject.renderer.material.color = new Color (0, 0, 1);
		}


		//		iTween.MoveTo (NewNucleosome, new Vector3 ((StartPosition/3), 0, 0), 2);



		return NewNucleosome;
	}

}