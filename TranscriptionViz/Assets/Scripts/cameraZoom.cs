using UnityEngine;
using System.Collections;

public class cameraZoom : MonoBehaviour {

	public float zoomSpeed = 20;

	public float minZoom = 30;
	public float maxZoom = 150;

	void Update ()
	{

		float scroll = Input.GetAxis("Mouse ScrollWheel");
		if (scroll != 0.0f)
		{

				camera.fieldOfView -= scroll*zoomSpeed;

				camera.fieldOfView = Mathf.Clamp(camera.fieldOfView, minZoom, maxZoom);

				Debug.Log (camera.fieldOfView);

		}
	}

}
