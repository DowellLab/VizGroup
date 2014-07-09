using UnityEngine;
using System.Collections;

public class GUI_Stuff : MonoBehaviour
{
	public Color myColor;

	void OnGUI ()
	{
		myColor = RGBSlider (new Rect (10, 10, 200, 30), myColor);
	}

	Color RGBSlider (Rect screenRect, Color rgb)
	{

		rgb.r = CompoundControls.LabelSlider (screenRect, rgb.r, 1.0f, "Red");

		screenRect.y += 20;
		rgb.g = CompoundControls.LabelSlider (screenRect, rgb.g, 1.0f, "Green");

		screenRect.y += 20; 
		rgb.b = CompoundControls.LabelSlider (screenRect, rgb.b, 1.0f, "Blue");

		return rgb;
	}


}





	