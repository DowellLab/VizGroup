using UnityEngine;
using System.Text;
using System.Collections;
using System.Collections.Generic;

public class Obj
{
		public string type;
		public string subtype;
		public int pos;
		public int length;
		public string status;

		public Obj ()
		{
				type = "none";
				subtype = "none";
				pos = 0;
				length = 0;
				status = "none"; 
		}

		public Obj (string t, string st, int p, int l)
		{
				type = t;
				subtype = st;
				pos = p;
				length = l;
				status = "none";
		}
	
		public Obj (string t, string st, int p, int l, string s)
		{
				type = t;
				subtype = st;
				pos = p;
				length = l;
				status = s;
		}

		public void set (string t, string st, int p, int l)
		{
				this.type = t;
				this.subtype = st;
				this.pos = p;
				this.length = l;
		}



	

}

public class ObjList {

	public List<Obj> list;

	public ObjList () {
		list = new List<Obj>();
	}
}

