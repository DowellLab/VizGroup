using UnityEngine;
using System.Collections;

//Provides a control that has labeled slider 
public class CompoundControls : MonoBehaviour
{
	public static float LabelSlider (Rect screenRect, float sliderValue, float sliderMaxValue, string labelText, GUIStyle style)
	{
		GUI.Label (screenRect, labelText, style);

		// <- Push the slider to the end of the Label
		screenRect.x += screenRect.width;

		sliderValue = GUI.HorizontalSlider (screenRect, sliderValue, 0.0f, sliderMaxValue);
		return sliderValue;
	}

	public static string LabelTextField (Rect labelRect, string labelText, string textField, GUIStyle style)
	{
		GUI.Label (labelRect, labelText, style);


		// <- Push the slider to the end of the Label
		labelRect.x += labelRect.width;

		textField = GUI.TextField (new Rect(labelRect.x + 10, labelRect.y, labelRect.width, labelRect.height), textField);

		return textField;
	}
}

