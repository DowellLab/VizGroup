// Namespace Declaration
using System;
using System.IO;

public class Nucleosomes
{
	public int starting_position { get; set; }
	public string state { get; set; }

	public Nucleosomes(int start, string stt)
	{
		starting_position = start;
		state = stt;
	}
}


class TextParser
{
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

