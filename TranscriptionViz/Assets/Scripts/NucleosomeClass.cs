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

public class NucleosomeClass : ObjectsOnDNA
{

	public static Shader specular = Shader.Find("Specular");

	public NucleosomeClass(string maintype, string subtype, float startPosition, float length) : base(maintype, subtype, startPosition, length)
	{
		MainType = maintype;
		Subtype = subtype;
		StartPosition = startPosition;
		Length = length;

	}


	public static GameObject CreateNucleosome(ObjectsOnDNA Nucleosome)
	{

		GameObject NewNucleosome;

		NewNucleosome = GameObject.CreatePrimitive (PrimitiveType.Sphere);

		if (Nucleosome.StartPosition != 0) {
			NewNucleosome.transform.localScale = new Vector3 (Nucleosome.Length / 3.5f, Nucleosome.Length / 6f, Nucleosome.Length / 3.5f); // Scale extends on both sides, so is a bad ultimate choice
		} else {
			NewNucleosome.transform.localScale = new Vector3 (Nucleosome.Length / 3.5f, Nucleosome.Length / 3f, Nucleosome.Length / 3.5f);
		}

		NewNucleosome.renderer.material.shader = specular;

		Nucleosome.StartPosition += Nucleosome.Length / 4;

//		NewNucleosome.transform.position = new Vector3 ((Nucleosome.StartPosition / 3.5f) - 0.6f, 0.3f, 0);

		NewNucleosome.transform.position = new Vector3 (10, 25, 0);
		iTween.MoveTo (NewNucleosome, new Vector3 ((Nucleosome.StartPosition / 3.5f) - 0.6f, 0.3f, 0), 1.5f);

		NewNucleosome.name = "Nucleosome";
		NewNucleosome.tag = "Nucleosome";

		// Nucleosome Color
		if (Nucleosome.Subtype == "'Binding'")
		{
			NewNucleosome.gameObject.renderer.material.color = new Color (0.2f, 0.4f, 0.5f);

		} else if (Nucleosome.Subtype == "'Unbinding'") {

			NewNucleosome.gameObject.renderer.material.color = new Color (0, 1, 1);

		} else {

			NewNucleosome.gameObject.renderer.material.color = new Color (0, 0, 1);
		}
			

		return NewNucleosome;
	}

	public static void ChangeNuc(ObjectsOnDNA toChange, string newSub, float convertPos )
	{
		GameObject[] nucleosomes = GameObject.FindGameObjectsWithTag ("Nucleosome");

		foreach (GameObject nuc in nucleosomes)
		{
			if (nuc.transform.position.x == convertPos)
			{
				if (newSub == "'Binding'")
				{
					nuc.gameObject.renderer.material.color = new Color (0.2f, 0.4f, 0.5f);
				} else if (newSub == "'Unbinding'") {
					nuc.gameObject.renderer.material.color = new Color (0, 1, 1);
				} else if (newSub == "'Stable'") {
					nuc.gameObject.renderer.material.color = new Color (0, 0, 1);
				}
			}

		}

	}

}