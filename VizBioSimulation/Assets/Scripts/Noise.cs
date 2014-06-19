using UnityEngine;
using System.Collections;

public class Noise : MonoBehaviour
{	
	public static int numSpheres = 100;
	public double delay = 0;

	void Start(){

		for (int i = 0; i < numSpheres; i++) 
		{
			float randomNumber = Random.Range (5f, 30f);
			if(randomNumber < 15)
			{
				GameObject sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
				sphere.renderer.material.color = Color.blue;
				sphere.transform.position = new Vector3(22, 270, 1237);
				sphere.transform.localScale = new Vector3(10, 10, 10);
				iTween.MoveTo(sphere, iTween.Hash("path", iTweenPath.GetPath("PolygonPath"), "easeType", "easeInOutSine", "loopType", "pingpong", "time", randomNumber, "delay", delay));

			}
			else if(randomNumber < 20)
			{
				GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
				cube.renderer.material.color = Color.white;
				cube.transform.position = new Vector3(22, 270, 1237);
				cube.transform.localScale = new Vector3(10, 10, 10);
				iTween.MoveTo(cube, iTween.Hash("path", iTweenPath.GetPath("PolygonPath"), "easeType", "easeInOutSine", "loopType", "pingpong", "time", randomNumber, "delay", delay));

			}
			else if(randomNumber < 25)
			{
				GameObject capsule = GameObject.CreatePrimitive(PrimitiveType.Capsule);
				capsule.renderer.material.color = Color.yellow;
				capsule.transform.position = new Vector3(22, 270, 1237);
				capsule.transform.localScale = new Vector3(10, 10, 10);
				iTween.MoveTo(capsule, iTween.Hash("path", iTweenPath.GetPath("PolygonPath"), "easeType", "easeInOutSine", "loopType", "pingpong", "time", randomNumber, "delay", delay));
			}
			else
			{
				GameObject cylinder = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
				cylinder.renderer.material.color = Color.red;
				cylinder.transform.position = new Vector3(22, 270, 1237);
				cylinder.transform.localScale = new Vector3(10, 10, 10);
				iTween.MoveTo(cylinder, iTween.Hash("path", iTweenPath.GetPath("PolygonPath"), "easeType", "easeInOutSine", "loopType", "pingpong", "time", randomNumber, "delay", delay));
			}

			delay += .1;
			
		}


	}
}
