using System;
using System.IO;
using System.Text.RegularExpressions;
using System.Collections.Generic;

public class simParams
{


		private void add_section(string section)
		{
			if (!dict.ContainsKey (section)) {
				dict.Add (section, new Dictionary<string, object> ());
				//Console.WriteLine ("\nAdded new section {0}.\n", section);
			}
		}
		

		//DATA STRUCTURE---------------------------------	
		public Dictionary<string, Dictionary<string, object>> dict;				//Data structure holding all parameters
		
			
		public simParams()																//CONSTRUCTOR
		{
			dict = new Dictionary<string, Dictionary<string, object>> ();
		}

			
		public simParams(simParams s)													//COPY CONSTRUCTOR	
		{
			
			dict = new Dictionary<string, Dictionary<string, object>> ();

			foreach(KeyValuePair<string, Dictionary<string, object>> sec in s.dict)
			{
				dict.Add(sec.Key, new Dictionary<string, object>());
				foreach(KeyValuePair<string, object> attr in s.dict[sec.Key])
				{
					dict[sec.Key].Add(attr.Key, attr.Value);
				}
			}
		}

		//Initialize defaults
		public void initialize_defaults()
		{
			dict.Add ("TRAPP", new Dictionary<string, object> ());
			dict.Add ("NUCLEOSOME", new Dictionary<string, object> ());
			dict.Add ("RNAP", new Dictionary<string, object> ());
		}

		//SET METHODS--------------------------------------
		public void add_int(string section, string attribute, int value)
		{
			if (!dict.ContainsKey (section)) {
				add_section (section);
		 	}

			else {
				dict[section].Add (attribute, value);
				
			}
		}

		public void add_float(string section, string attribute, float value)
		{
			if (!dict.ContainsKey (section)) {
				add_section (section);
			}
			
			else {
				dict[section].Add (attribute, value);
			}
		}

		public void add_string(string section, string attribute, string value)
		{
			if (!dict.ContainsKey (section))	{
				add_section (section);
			}
			
			else {
				dict[section].Add (attribute, value);
			}
		}

		//GET METHODS--------------------------------------
		public int get_int(string section, string attribute)
		{
			if (!dict.ContainsKey (section)) {
				Console.WriteLine ("!Error! section {0} does not exist.\n", section);
				return -1;
			}
			
			else {
				return (int)dict[section][attribute];
			}
		}

		public float get_float(string section, string attribute)
		{
			if (!dict.ContainsKey (section)) {
				Console.WriteLine ("!Error! section {0} does not exist.\n", section);
				return -1.0f;
			}
			
			else {
				return (float)dict[section][attribute];
			}
		}

		public string get_string(string section, string attribute)
		{
			if (!dict.ContainsKey (section)) {
				Console.WriteLine ("!Error! section {0} does not exist.\n", section);
				return "NULL";
			}
			
			else {
				return (string)dict[section][attribute];
			}
		}


		public void get_section(string section)
		{
		Console.WriteLine ("Showing attributes for section '{0}'", section);
		foreach (KeyValuePair<string, object> sec in dict[section])
			Console.WriteLine (" '{0}' : '{1}'", sec.Key, sec.Value);
		}



		//FILE IO METHODS--------------------------------------
		public void write(string filename)
		{

			StreamWriter wstream = new StreamWriter(filename);

			foreach(KeyValuePair<string, Dictionary<string, object>> sec in dict)
			{
				wstream.WriteLine("\n[{0}]", sec.Key);
				foreach(KeyValuePair<string, object> attr in dict[sec.Key])
				{
					wstream.WriteLine("{0} = {1}", attr.Key, attr.Value);
				}

			}

			wstream.Close ();
		}




		public void read(string filename)
		{
			bool readingSection = false;											// true - reading within section, false - not reading within a section
			string sectionBuffer = "Default Section";
			string buffer;
			Match m;
			string sectionMarkerPattern = @"\[(.*?)\]";								// Matches within square brackets 

			//Parsing variables
			string[] splitByComments; 
			string[] splitByEqualSign; 



			StreamReader read = File.OpenText (filename);

			while (!read.EndOfStream)
			{
				//Read one line of .ini file at a time
				buffer = read.ReadLine();	
				
				if(buffer == "")							//If read in blank, skip iteration
					continue;


				m = Regex.Match(buffer, sectionMarkerPattern);					//Pattern match to a new section
				if(m.Success)  														
				{	
					sectionBuffer = m.Groups[1].Value;
					add_section(sectionBuffer); 
					readingSection = true;
				}
				
				else 															
				{
					if(readingSection)											//Parsing attributes inside a section
					{	
						//Ignore things to the right of comments
						char[] splitter1 = new char[] {'#'};
						splitByComments = buffer.Split(splitter1, 2, StringSplitOptions.None);  
						if(splitByComments[0] == "")
							continue;

						//Parsing on on sides of equal sign
						char[] splitter2 = new char[] {'='};
						splitByEqualSign = splitByComments[0].Split(splitter2, 50, StringSplitOptions.RemoveEmptyEntries);
						if(splitByEqualSign.Length > 1)
						add_string(sectionBuffer, splitByEqualSign[0].Trim (), splitByEqualSign[1].Trim ());
					}

					else 														//We're not reading in a section														 
					{
						Console.WriteLine ("No data extracted for line '{0}', proceeding...\n", buffer);
					}
						
					
				}
				
			}
				read.Close ();

		}



		
}

