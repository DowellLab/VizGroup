using UnityEngine;
using System.Collections;

public class CompoundControls : MonoBehaviour
{
	public static float LabelSlider (Rect screenRect, float sliderValue, float sliderMaxValue, string labelText)
	{
		GUI.Label (screenRect, labelText);

		// <- Push the slider to the end of the Lable
		screenRect.x += screenRect.width;

		sliderValue = GUI.HorizontalSlider (screenRect, sliderValue, 0.0f, sliderMaxValue);
		return sliderValue;
	}
}

