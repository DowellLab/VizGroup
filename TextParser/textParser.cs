// Namespace Declaration
using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;



class TextParser
{
	// Reads in a string (a timestep) with format [(type, subtype, position, length), (type, subtype, position, length)...].
	// It takes each component (type, subtype, position, length) and separates out the components into a list of strings called 'ObjectArray'.
	public static void read_time_step(string input)
	{
		string pattern = @"\(((.*?))\)";
		string[] ObjectArray;
		
		foreach(Match match in Regex.Matches(input, pattern, RegexOptions.IgnoreCase))
		{
			string intermediateString1 = Regex.Replace(match.Value, "[.,()]?", "");

			ObjectArray = (intermediateString1).Split (new Char[] {' '});
			Console.WriteLine("Found type: '{0}', Found subtype: '{1}', Found position: '{2}', Found length '{3}'", ObjectArray[0], ObjectArray[1], ObjectArray[2], ObjectArray[3]);
			Console.WriteLine();
		}	
	}

	static void Main()
	{
		Console.WriteLine("Reading the contents from the test file\n");

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

