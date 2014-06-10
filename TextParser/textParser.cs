// Namespace Declaration
using System;
using System.IO;



class TextParser
{
	// Reads in a string (a timestep) with format [(type, position, length), (type, position, length)...].
	// It takes each component (type, position, length) and separates out the components into a list of strings called 'ar'.
	public static void read_time_step(string s)
	{
		string pattern = @"\(((.*?))\)";
		string[] ar;
		
		foreach(Match match in Regex.Matches(s, pattern, RegexOptions.IgnoreCase))
		{
			ar = (match.Value).Split (new Char[] {' '});
			Console.WriteLine("Found type: '{0}', Found position: '{1}', Found length '{2}'", ar[0], ar[1], ar[2]);
			Console.WriteLine();
		}	
	}

	static void Main()
	{
		Console.WriteLine("Reading the contents from the test.txt file\n");

		// Use stream object to open and read file
		StreamReader s = File.OpenText ("test2.txt");

		//string 'buffer' used to hold streamed 
		string read = null;

		// Search Target = String we want to locate
		string searchTarget = "hello";


		//*************PARSING LOGIC************//
		
		
		while((read = s.ReadLine()) != null)		//Reads the whole line
		{
			
			if (read.Contains (searchTarget)) 
			{
				// Should find EACH instance of searchTarget
				
				Console.WriteLine (searchTarget);	// Currently writes first instance of searchTarget
				
				Console.WriteLine(read.IndexOf(searchTarget));	// Currently writes position in string of first instance of searchTarget
			}
			
		}
				
		//**************************************//*
		s.Close();
	}


	

}

