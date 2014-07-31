using UnityEngine;
using System.Collections;

public class cameraScroll : MonoBehaviour {

	public int scrollArea;
	private float scrollSpeed;
	public float scrollForce;
	
	// Use this for initialization
	void Start () 
	{
		scrollArea = 50;
		scrollSpeed = 1;
		scrollForce = 10;
	}


	// Update is called once per frame
	void Update () 
	{
		//Scroll  push, means it screen movement will accelerate
		scrollSpeed += (scrollForce * Time.deltaTime);



		var mPosX = Input.mousePosition.x;
		var mPosY = Input.mousePosition.y;


		// Do camera movement by mouse position
		if (mPosX < scrollArea) {transform.Translate(Vector3.right * -scrollSpeed * Time.deltaTime);}
		if (mPosX >= Screen.width-scrollArea) {transform.Translate(Vector3.right * scrollSpeed * Time.deltaTime);}
		if (mPosX > scrollArea & mPosX < Screen.width - scrollArea) { scrollSpeed = 0; }
	}
}
