using System;
using System.IO;
using System.Text.RegularExpressions;
using System.Collections.Generic;

public class simParams
{


		private void add_section(string section)
		{
			if (!dict.ContainsKey (section)) {
				dict.Add (section, new SortedDictionary<string, string> ());
				//Console.WriteLine ("\nAdded new section {0}.\n", section);
			}
		}
		

		//DATA STRUCTURE---------------------------------	
		public SortedDictionary<string, SortedDictionary<string, string>> dict;				//Data structure holding all parameters
		
			
		public simParams()																	//CONSTRUCTOR
		{
			dict = new SortedDictionary<string, SortedDictionary<string, string>> ();
		}
	
		public simParams(simParams s)														//COPY CONSTRUCTOR	
		{
			
			dict = new SortedDictionary<string, SortedDictionary<string, string>> ();

			foreach(KeyValuePair<string, SortedDictionary<string, string>> sec in s.dict)
			{
				dict.Add(sec.Key, new SortedDictionary<string, string>());
				foreach(KeyValuePair<string, string> attr in s.dict[sec.Key])
				{
					dict[sec.Key].Add(attr.Key, attr.Value);
				}
			}
		}

	
		//Initialize defaults
		public List<string> initialize_defaults()
		{

			List<string> sectionList = new List<string> ();
			dict.Add ("TRAPP", new SortedDictionary<string, string> ());
				add_string ("TRAPP", "NAME", "");
				add_string ("TRAPP", "CHR", "");
				add_string ("TRAPP", "COMMENT", "");
				add_string ("TRAPP", "END", "");
				add_string ("TRAPP", "START", "");
				add_string ("TRAPP", "TF_LIST", "");
				add_string ("TRAPP", "TIMESTEPS", "");
			dict.Add ("NUCLEOSOME", new SortedDictionary<string, string> ());
				add_string ("NUCLEOSOME", "INITIAL_COUNT", "");
				add_string ("NUCLEOSOME", "MIN_LINKER_SIZE", "");
				add_string ("NUCLEOSOME", "ON_RATE", "");
			dict.Add ("RNAP", new SortedDictionary<string, string> ());
				add_string ("RNAP", "INITIAL_COUNT", "");
				add_string ("RNAP", "N_INIT_STAGES", "");
				add_string ("RNAP", "ON_RATE", "");
				add_string ("RNAP", "TRANSCRIPTION_RATE", "");

			
			sectionList.Add ("TRAPP");
			sectionList.Add ("NUCLESOME");
			sectionList.Add ("RNAP");

		return sectionList;

		}



		//SET METHODS--------------------------------------
		public void add_int(string section, string attribute, int value)
		{
			if (!dict.ContainsKey (section)) 
				add_section (section);
	 		

			if (!dict [section].ContainsKey (attribute))
					dict [section].Add (attribute, value.ToString());
				else
					dict [section] [attribute] = value.ToString();
		}

		public void add_float(string section, string attribute, float value)
		{
			if (!dict.ContainsKey (section)) 
				add_section (section);

			
			if (!dict [section].ContainsKey (attribute))
					dict [section].Add (attribute, value.ToString());
				else
					dict [section] [attribute] = value.ToString();
		}

		public void add_string(string section, string attribute, string value)
		{
			if (!dict.ContainsKey (section))	
				add_section (section);
			
			
			if (!dict [section].ContainsKey (attribute))
					dict [section].Add (attribute, value);
				else
					dict [section] [attribute] = value;
		}



		//REMOVE METHODS--------------------------------------

		public void remove_section(string section)
		{
			if(dict.ContainsKey(section))
			{
				foreach (KeyValuePair<string, string> sec in dict[section]) 
				{
					dict[section].Remove(sec.Key);
				}
				dict.Remove(section);
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
				return Convert.ToInt32(dict[section][attribute]);
			}
		}

		public float get_float(string section, string attribute)
		{
			if (!dict.ContainsKey (section)) {
				Console.WriteLine ("!Error! section {0} does not exist.\n", section);
				return -1.0f;
			}
			
			else {
				return Convert.ToSingle(dict[section][attribute]);
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
		foreach (KeyValuePair<string, string> sec in dict[section])
			Console.WriteLine (" '{0}' : '{1}'", sec.Key, sec.Value);
		}

		


		//FILE IO METHODS--------------------------------------
		public void write(string filename)
		{

			StreamWriter wstream = new StreamWriter(filename);

			foreach(KeyValuePair<string, SortedDictionary<string, string>> sec in dict)
			{
				wstream.WriteLine("\n[{0}]", sec.Key);
				foreach(KeyValuePair<string, string> attr in dict[sec.Key])
				{
					wstream.WriteLine("{0} = {1}", attr.Key, attr.Value);
				}

			}

			wstream.Close ();
		}
	
		public List<string> read(string filename)
		{
			bool readingSection = false;											// true - reading within section, false - not reading within a section
			string sectionBuffer = "Default Section";
			List<string> sectionList = new List<string>();
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
				
				if(buffer == "")												//If read in blank, skip iteration
					continue;


				m = Regex.Match(buffer, sectionMarkerPattern);					//Pattern match to a new section
				if(m.Success)  														
				{	
					sectionBuffer = m.Groups[1].Value;
					add_section(sectionBuffer); 
					sectionList.Add(sectionBuffer);
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
				return sectionList;
		}



		
}

