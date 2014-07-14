using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class DoublyLinkedList : MonoBehaviour {

	public LinkedList<ObjList> timesteps;
	public LinkedListNode<Obj> cursor;

	//constructor
	public DoublyLinkedList() {
		timesteps = new LinkedList<ObjList>(); 

	}
	/*
	//prints entire linked list
	public void printList() {
		int index = 0;
		LinkedListNode<Obj> tempCursor = cursor;
		cursor = timesteps.First;

		while (cursor != null) {
			Debug.Log("Node Index: " + index);
			printNode (cursor);
			cursor = cursor.Next;
			index++;
		}

		Debug.Log ("List Count: " + timesteps.Count);
		cursor = tempCursor;
	}

	//prints provided node values
	public void printNode(LinkedListNode<Obj> lln) {
		Debug.Log("Type: " + lln.Value.type + 
		          " / Subtype: " + lln.Value.subtype + 
		          " / Position: " + lln.Value.pos + 
		          " / Length: " + lln.Value.length + 
		          " / Status: " + lln.Value.status);
	}
	*/

	// Use this for initialization
	void Start () {

		Obj n1 = new Obj ("chad", "bryan", 1, -1);
		Obj n2 = new Obj ("chad", "bryan", 2, -2);
		Obj n3 = new Obj ("chad", "bryan", 3, -3);
		DoublyLinkedList TSList = new DoublyLinkedList();
		ObjList chad = new ObjList ();
		chad.list.Add (n1);
		Debug.Log (chad.list [0]);

		//TSList[0].timesteps.AddFirst (n1);
		//TSList



	}
	
	// Update is called once per frame
	void Update () {
	
	}
}
