// Namespace Declaration
using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.Reflection;



class TextParser
{
	// Reads in a string (a timestep) with format [(type, subtype, position, length), (type, subtype, position, length)...].
	// It takes each component (type, subtype, position, length) and separates out the components into a list of strings called 'IntermediateArray'.
	public static void read_time_step(string input)
	{
		string pattern = @"\(((.*?))\)";
		string intermediateString1 = "";
		string[] IntermediateArray = (intermediateString1).Split (new Char[] {' '});
		List<string> ObjectList;

		ObjectList = new List<string> ();

		foreach(Match match in Regex.Matches(input, pattern, RegexOptions.IgnoreCase))
		{
			intermediateString1 = Regex.Replace(match.Value, "[.,()]?", "");
		
			IntermediateArray = (intermediateString1).Split (new Char[] {' '});
			ObjectList.AddRange (IntermediateArray);

		}	
			
		// ObjectList currently holds all elements for all timesteps. How do you split them up?

		foreach (var listItem in ObjectList) 
		{
			Console.WriteLine("ObjectList Element '{0}'", listItem);
			Console.WriteLine(listItem);
			Console.WriteLine ();
		}

//		Console.WriteLine("Found type: '{0}', Found subtype: '{1}', Found position: '{2}', Found length '{3}'", ObjectList[0], ObjectList[1], ObjectList[2], ObjectList[3]);

//		Console.WriteLine("Found type: '{0}', Found subtype: '{1}', Found position: '{2}', Found length '{3}'", ObjectList[4], ObjectList[5], ObjectList[6], ObjectList[7]);
//		Console.WriteLine("Found type: '{0}', Found subtype: '{1}', Found position: '{2}', Found length '{3}'", ObjectList[8], ObjectList[9], ObjectList[10], ObjectList[11]);
//		Console.WriteLine("Found type: '{0}', Found subtype: '{1}', Found position: '{2}', Found length '{3}'", ObjectList[12], ObjectList[13], ObjectList[14], ObjectList[15]);


	}

	static void Main()
	{
		//Console.WriteLine("Reading the contents from the test file\n");

		// Use stream object to open and read file
		StreamReader s = File.OpenText ("test3.txt");

		//string 'buffer' used to hold streamed 
		string read = null;

		//*************PARSING LOGIC************//
		
		
		while((read = s.ReadLine()) != null)		//Reads the whole line
		{

			read_time_step (read);	
			
		}
				
		//**************************************//*
	
		s.Close();
	}


	

}

