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
//		foreach (var listItem in ObjectList) 
//		{
//			int i = 0;
//			Console.WriteLine("ObjectList Element '{0}'", i);
//			i++;
//			Console.WriteLine(listItem);
//			Console.WriteLine ();
//		}
//

		// Prints out the contents for just the first timestep!!!
		for (int i=0; i < 1000; i= i + 4) 
		{
			if (ObjectList [i] != null) {
				Console.WriteLine("Found type: '{0}', Found subtype: '{1}', Found position: '{2}', Found length '{3}'", ObjectList[i], ObjectList[i + 1], ObjectList[i + 2], ObjectList[i + 3]);
				Console.WriteLine ();
			} else {
				Console.WriteLine ("No more!");
			}
				
		}
			
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

