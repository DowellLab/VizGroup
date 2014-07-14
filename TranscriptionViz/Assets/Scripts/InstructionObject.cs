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


public class InstructionObject {

	public GameObject TranscriptionSimObject;
	public string instruction;

	public InstructionObject(GameObject TO, string instruct)
	{
		TranscriptionSimObject = TO;
		instruction = instruct;
	}

}
