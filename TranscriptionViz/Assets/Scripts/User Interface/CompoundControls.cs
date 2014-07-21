using UnityEngine;
using System.Collections;

//Provides a control that has labeled slider 
public class CompoundControls : MonoBehaviour
{
	public static float LabelSlider (Rect screenRect, float sliderValue, float sliderMaxValue, string labelText)
	{
		GUI.Label (screenRect, labelText);

		// <- Push the slider to the end of the Label
		screenRect.x += screenRect.width;

		sliderValue = GUI.HorizontalSlider (screenRect, sliderValue, 0.0f, sliderMaxValue);
		return sliderValue;
	}

	public static string LabelTextField (Rect labelRect, string labelText, string textField)
	{
		GUI.Label (labelRect, labelText);


		// <- Push the slider to the end of the Label
		labelRect.x += labelRect.width;

		textField = GUI.TextField (new Rect(labelRect.x + 10, labelRect.y, 20,labelRect.height), textField);

		return textField;
	}
}

