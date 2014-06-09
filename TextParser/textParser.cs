// Namespace Declaration
using System;
using System.IO;

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
		string searchTarget = "Hello";


		//*************PARSING LOGIC************//


		while((read = s.ReadLine()) != null)		//Reads the whole line
		{

			if (read.Contains (searchTarget)) 
			{
				Console.WriteLine (searchTarget);
			}

		}



		//**************************************//
		s.Close();
	}


	

}

