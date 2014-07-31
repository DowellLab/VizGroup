using UnityEngine;
using System.Collections;

public class cameraScroll : MonoBehaviour {

	public int scrollArea;
	private float scrollSpeed;
	public float scrollForce;
	private float dTime;
	
	// Use this for initialization
	void Start () 
	{
		scrollArea = 30;
		scrollSpeed = 5;
		scrollForce = 10;
		dTime = 0.0035f;
	}


	// Update is called once per frame
	void Update () 
	{
		//Scroll  push, means it screen movement will accelerate
		scrollSpeed += (scrollForce * dTime);



		var mPosX = Input.mousePosition.x;
		var mPosY = Input.mousePosition.y;


		// Do camera movement by mouse position
		if (mPosX < scrollArea) {transform.Translate(Vector3.right * -scrollSpeed * dTime);}
		if (mPosX >= Screen.width-scrollArea) {transform.Translate(Vector3.right * scrollSpeed * dTime);}
		if (mPosX > scrollArea & mPosX < Screen.width - scrollArea) { scrollSpeed = 5; }
	}
}
