using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class DoublyLinkedList : MonoBehaviour {

	public LinkedList<Obj> timesteps;
	public LinkedListNode<Obj> cursor;

	public DoublyLinkedList() {
		timesteps = new LinkedList<Obj>(); 

	}

	public void printNode(LinkedListNode<Obj> lln) {
		Debug.Log("Type: " + lln.Value.type + " / Subtype: " + lln.Value.subtype + " / Position: " + lln.Value.pos + " / Length: " + lln.Value.length);
	}

	// Use this for initialization
	void Start () {

		Obj n1 = new Obj ("chad", "bryan", 1, -1);
		Obj n2 = new Obj ("chad", "bryan", 2, -2);
		Obj n3 = new Obj ("chad", "bryan", 3, -3);
		LinkedList<Obj> TSList = new LinkedList<Obj>();
		TSList.AddFirst (n1);
		TSList.AddFirst (n2);
		TSList.AddFirst (n3);
		LinkedListNode<Obj> head = TSList.First; 
		Debug.Log (head.Value.length);
		head = head.Next.Next; 
		Debug.Log (head.Value.length);

		timesteps.AddFirst (n1);
		cursor = timesteps.First;
		printNode (cursor);


	}
	
	// Update is called once per frame
	void Update () {
	
	}
}
