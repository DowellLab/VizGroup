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


public class InstructionObject
{

	public ObjectsOnDNA TranscriptionSimObject;
	public string instruction;

	public static List<InstructionObject> InstructionList;

	// Constructor
	public InstructionObject(ObjectsOnDNA TO, string instruct)
	{
		TranscriptionSimObject = TO;
		instruction = instruct;
	}

	// Create List of Instruction Objects to insert as node into DoublyLinkedList
	public static List<InstructionObject> CreateInstructList(InstructionObject toInsert)
	{
		InstructionList = new List<InstructionObject>();
		InstructionList.Add (toInsert);

		foreach (InstructionObject testing in InstructionList)
		{
			Debug.Log (testing.TranscriptionSimObject.MainType + " " + testing.TranscriptionSimObject.Subtype + " " + testing.TranscriptionSimObject.StartPosition);
		}

		return InstructionList;
	}

}
