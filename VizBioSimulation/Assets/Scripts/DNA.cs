using UnityEngine;
using System.Collections;
using System;
using System.IO;
using System.Text;
public class DNA : MonoBehaviour {


	public string type;
	public string subtype;
	public int position;
	public int length;

	protected FileInfo theSourceFile = null;
	protected StreamReader reader = null;
	protected string text = " "; // assigned to allow first line to be read below
	
	public DNA (string t, string st, int pos, int l){
		type = t;
		subtype = st;
		position = pos;
		length = l;
	}

	void printDNA (){
		Debug.Log (this.type + ", " + this.subtype + ", " + this.position.ToString () + ", " + this.length.ToString ());		
	}

	// Use this for initialization
	void Start () {

		DNA dna = new DNA ("chad", "bryant", 22, 6);
		dna.printDNA ();
		theSourceFile = new FileInfo ("DNA.txt");
		reader = theSourceFile.OpenText();	

	}
	
	// Update is called once per frame
	void Update () {
		if (text != null) {
			text = reader.ReadLine();
			//Console.WriteLine(text);
			print (text);
		}
	
	}
}

/*
public class LineReader : MonoBehaviour
{
	protected FileInfo theSourceFile = null;
	protected StreamReader reader = null;
	protected string text = " "; // assigned to allow first line to be read below
	
	void Start () {
		theSourceFile = new FileInfo ("Test.txt");
		reader = theSourceFile.OpenText();
	}
	
	void Update () {
		if (text != null) {
			text = reader.ReadLine();
			//Console.WriteLine(text);
			print (text);
		}
	}
}
*/
