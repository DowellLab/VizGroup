using UnityEngine;
using System.Text;
using System.Collections;

public class Obj
{
		public string type;
		public string subtype;
		public int pos;
		public int length;

		public Obj ()
		{
				type = "none";
				subtype = "none";
				pos = 0;
				length = 0;
		}

		public Obj (string t, string st, int p, int l)
		{
				type = t;
				subtype = st;
				pos = p;
				length = l;
		}

		public void set (string t, string st, int p, int l)
		{
				this.type = t;
				this.subtype = st;
				this.pos = p;
				this.length = l;
		}

		//public void print()
		//{
		//Console.WriteLine (this.type + " " + this.subtype + " " + this.pos + " " + this.length); 
		//}


	

}
// Use this for initialization
//void Start ()
//{
//Node n1 = new Node ("TF", "REB1", 22, 3);
//n1.print ();
//n1.set ("yeah!", "no!", 1, 2);
//n1.print ();
	
//}

//}
