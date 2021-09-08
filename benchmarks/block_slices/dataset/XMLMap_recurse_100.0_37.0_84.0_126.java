private static void recurse(Map<String, Object> tm, String path, Node parentNode, boolean doFull, int d) 
	{
		doDebug(d,"> recurse path="+path+" parentNode="+ nodeToString(parentNode));
		d++;

		NodeList nl = parentNode.getChildNodes();
		NamedNodeMap nm = parentNode.getAttributes();

		// Count the TextNodes
		int nodeCount = 0;
		String value = null;
		
		// Insert the text node if we find one
		if ( nl != null ) for (int i = 0; i< nl.getLength(); i++ ) {
			Node node = nl.item(i);
			if (node.getNodeType() == node.TEXT_NODE) {
				value = node.getNodeValue();
				if ( value == null ) break;
				if ( value.trim().length() < 1 ) break;
				// doDebug(d,"Adding path="+path+" value="+node.getNodeValue());
				tm.put(path,node.getNodeValue());
				break;  // Only the first one
			}
		}
		
		// Now loop through and add the attribute values 
		if ( nm != null ) for (int i = 0; i< nm.getLength(); i++ ) {
			Node node = nm.item(i);
			if (node.getNodeType() == node.ATTRIBUTE_NODE) {
				String name = node.getNodeName();
				value = node.getNodeValue();
				// doDebug(d,"ATTR "+path+"("+name+") = "+node.getNodeValue());
				if ( name == null || name.trim().length() < 1 || 
						value == null || value.trim().length() < 1 ) continue;  

				String newPath = path+"!"+name;
				tm.put(newPath,value);
			}
		}
		
		// If we are not doing the full DOM - we only traverse the first child
		// with the same name - so we use a set to record which nodes 
		// we have gone down.
		if ( ! doFull ) {
			// Now descend the tree to the next level deeper !!
			Set <String> done = new HashSet<String>();
			if ( nl != null ) for (int i = 0; i< nl.getLength(); i++ ) {
				Node node = nl.item(i);
				if (node.getNodeType() == node.ELEMENT_NODE && ( ! done.contains(node.getNodeName())) ) {
					doDebug(d,"Going down the rabbit hole path="+path+" node="+node.getNodeName());
					recurse(tm, addSlash(path)+node.getNodeName(),node,doFull,d);
					doDebug(d,"Back from the rabbit hole path="+path+" node="+node.getNodeName());
					done.add(node.getNodeName());	
				}
			}
			d--;
			doDebug(d,"< recurse path="+path+" parentNode="+ nodeToString(parentNode));
			return;
		}

		// If we are going to do the full expansion - we need to know when 
		// There are more than one child with the same name.  If there are more
		// One child, we make list of Maps.

		Map<String,Integer> childMap = new TreeMap<String,Integer>();
		if ( nl != null ) for (int i = 0; i< nl.getLength(); i++ ) {
			Node node = nl.item(i);
			if (node.getNodeType() == node.ELEMENT_NODE ) {
				Integer count = childMap.get(node.getNodeName());
				if ( count == null ) count = new Integer(0);
				count = count + 1;
				// Insert or Replace
				childMap.put(node.getNodeName(), count);
			}
		}
		
		if ( childMap.size() < 1 ) return;
		
		// Now go through the children nodes and make a List of Maps
		Iterator<String> iter = childMap.keySet().iterator();
		Map<String,List<Map<String,Object>>> nodeMap = new TreeMap<String,List<Map<String,Object>>>();
		while ( iter.hasNext() ) {
			String nextChild = iter.next();
			if ( nextChild == null ) continue;
			Integer count = childMap.get(nextChild);
			if ( count == null ) continue;
			if ( count < 2 ) continue;
			doDebug(d,"Making a List for "+nextChild);
			List<Map<String,Object>> newList = new ArrayList<Map<String,Object>>();
			nodeMap.put(nextChild,newList);
		}
		
		// Now descend the tree to the next level deeper !!
		if ( nl != null ) for (int i = 0; i< nl.getLength(); i++ ) {
			Node node = nl.item(i);
			if (node.getNodeType() == node.ELEMENT_NODE ) {
				String childName = node.getNodeName();
				if ( childName == null ) continue;
				List<Map<String,Object>> mapList = nodeMap.get(childName);
				if ( mapList == null ) {
					doDebug(d,"Going down the single rabbit hole path="+path+" node="+node.getNodeName());
					recurse(tm, addSlash(path)+node.getNodeName(),node,doFull,d);
					doDebug(d,"Back from the single rabbit hole path="+path+" node="+node.getNodeName());
				} else {
					doDebug(d,"Going down the multi rabbit hole path="+path+" node="+node.getNodeName());
					Map<String,Object> newMap = new TreeMap<String,Object>();
					recurse(newMap,"/",node,doFull,d);
					doDebug(d,"Back from the multi rabbit hole path="+path+" node="+node.getNodeName()+" map="+newMap);
					if ( newMap.size() > 0 ) mapList.add(newMap);
				}
			}
		}
		
		// Now append the multi-node maps to our current map
		Iterator<String> iter2 = nodeMap.keySet().iterator();
		while ( iter2.hasNext() ) {
			String nextChild = iter2.next();
			if ( nextChild == null ) continue;
			List<Map<String,Object>> newList = nodeMap.get(nextChild);
			if ( newList == null ) continue;
			if ( newList.size() < 1 ) continue;
			doDebug(d,"Adding sub-map name="+nextChild+" list="+newList);
			tm.put(path+"/"+nextChild, newList);
		}
		d--;
        doDebug(d,"< recurse path="+path+" parentNode="+ nodeToString(parentNode));
	}