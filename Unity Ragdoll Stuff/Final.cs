using UnityEngine;
using UnityEditor;
using System.Collections;

public class Final : MonoBehaviour
{
	
	public GameObject MainCharacter;
	public GameObject MainCharacter_MeshRender;
	public float MainCharacterPos_X;
	public float MainCharacterPos_Y;
	public float MainCharacterPos_Z;
	public float MainCharacterRot_X;
	public float MainCharacterRot_Y;
	public float MainCharacterRot_Z;
	
	// Use this for initialization
	void Start ()
	{
		
		//Change the Mesh Renderers Bounding Box
		
		//Get the new Center for the Bounding Box
		float xC = MainCharacter_MeshRender.GetComponent<SkinnedMeshRenderer> ().localBounds.center.x;
		float yC = MainCharacter_MeshRender.GetComponent<SkinnedMeshRenderer> ().localBounds.center.y;
		float zC = MainCharacter_MeshRender.GetComponent<SkinnedMeshRenderer> ().localBounds.center.z;
		
		Vector3 newCenter = new Vector3 (xC, yC, zC);
		
		//Get the new Extents for the bounding box
		float x = ((MainCharacter_MeshRender.GetComponent<SkinnedMeshRenderer> ().localBounds.extents.x * 2) * 1.1f);
		float y = ((MainCharacter_MeshRender.GetComponent<SkinnedMeshRenderer> ().localBounds.extents.y * 2) * 1.1f);
		float zz = ((MainCharacter_MeshRender.GetComponent<SkinnedMeshRenderer> ().localBounds.extents.z * 2) * 1.1f);
		
		Vector3 newExtend = new Vector3 (x, y, zz);
		
		//Create a new Bounds
		Bounds newBounds = new Bounds (newCenter, newExtend);
		
		Debug.Log (newBounds);
		
		//Set the Current Bounds = new Bounds
		MainCharacter_MeshRender.GetComponent<SkinnedMeshRenderer> ().localBounds = newBounds;
	

		// create the prefab, and connect the dummy prefab root to it
		GameObject prefabRoot = new GameObject("MainCharacter");
		gameObject.transform.parent = prefabRoot.transform;
		Object prefab = EditorUtility.CreateEmptyPrefab("Assets/test.prefab");
		EditorUtility.ReplacePrefab(prefabRoot, prefab, ReplacePrefabOptions.ConnectToPrefab);

	}
	
	// Update is called once per frame
	void Update ()
	{

		MainCharacterPos_X = MainCharacter.transform.position.x;
		MainCharacterPos_Y = MainCharacter.transform.position.y;
		MainCharacterPos_Z = MainCharacter.transform.position.z;
		
		
		MainCharacterRot_X = MainCharacter.transform.rotation.x;
		MainCharacterRot_Y = MainCharacter.transform.rotation.y;
		MainCharacterRot_Z = MainCharacter.transform.rotation.z;
		
	}

}
