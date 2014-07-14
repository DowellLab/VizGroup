using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class DoublyLinkedList : MonoBehaviour {

	public LinkedList<InstructionObject> timestepLinkedList;
	public LinkedListNode<InstructionObject> cursor;



	//constructor
	public DoublyLinkedList() {
		timestepLinkedList = new LinkedList<InstructionObject>(); 


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

<<<<<<< HEAD
	public void printNode(LinkedListNode<InstructionObject> lln) {
//		Debug.Log("Type: " + lln.Value.type + " / Subtype: " + lln.Value.subtype + " / Position: " + lln.Value.pos + " / Length: " + lln.Value.length);
=======

>>>>>>> 343bd19cdbc71381c9a3b4eab868efd796b137a0
	}
	*/

	// Use this for initialization
	void Start () {


//		Obj n1 = new Obj ("chad", "bryan", 1, -1);
//		Obj n2 = new Obj ("chad", "bryan", 2, -2);
//		Obj n3 = new Obj ("chad", "bryan", 3, -3);
//		LinkedList<InstructionObject> TSList = new LinkedList<InstructionObject>();
//		TSList.AddFirst (n1);
//		TSList.AddFirst (n2);
//		TSList.AddFirst (n3);
//		LinkedListNode<Obj> head = TSList.First; 
//		Debug.Log (head.Value.length);
//		head = head.Next.Next; 
//		Debug.Log (head.Value.length);
//
//		timestepLinkedList.AddFirst (n1);
//		cursor = timestepLinkedList.First;
//		printNode (cursor);

	}
	
	// Update is called once per frame
	void Update () {
	
	}
}
