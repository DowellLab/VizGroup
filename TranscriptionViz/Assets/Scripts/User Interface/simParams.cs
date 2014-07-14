using UnityEngine;
using System;
using System.IO;
using System.Collections.Generic;

class simParams
{
	public class clssimParams
	{
		//Dictionary of data
		public Dictionary<string, Dictionary<string, int>> dict;


		public clssimParams()
		{
			dict = new Dictionary<string, Dictionary<string, int>> ();

			dict.Add ("DNA", new Dictionary<string, int> ());

			dict ["DNA"].Add ("count", 3);
			dict ["DNA"].Add ("color", 4);
			dict ["DNA"].Add ("size", 5);
		}

		public void test()
		{
			int n = dict["DNA"]["count"];

			Console.Write (n);

		}
	};

	static void main()
	{
		clssimParams c = new clssimParams ();
		c.test ();

	}

}