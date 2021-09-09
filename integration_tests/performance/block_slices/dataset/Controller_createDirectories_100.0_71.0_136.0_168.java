private static void createDirectories() throws FileNotFoundException {

	if(debug) log("Now in createDirectories()"); // NOI18N
	
	FileObject rootdir = 
	    FileUtil.getConfigRoot();
	if(debug) {
	    log("Root directory is " + rootdir.getName()); // NOI18N
	    File rootF = FileUtil.toFile(rootdir);
	    log("Root directory abs path " + // NOI18N
		rootF.getAbsolutePath());
	}

	FileLock lock = null;

	if(monDir == null || !monDir.isFolder()) {
	    try {
		monDir = rootdir.getFileObject(monDirStr);
	    }
	    catch(Exception ex) {
	    }
	    
	    if(monDir == null || !monDir.isFolder()) {
		if(monDir != null) {
		    try {
			lock = monDir.lock();
			monDir.delete(lock);
		    }
		    catch(FileAlreadyLockedException falex) {
			throw new FileNotFoundException();
		    }
		    catch(IOException ex) {
			throw new FileNotFoundException();
		    }
		    finally { 
			if(lock != null) lock.releaseLock();
		    }
		}
		try {
		    monDir = rootdir.createFolder(monDirStr);
		}
		catch(IOException ioex) {
		    if(debug) ioex.printStackTrace();
		}
	    }
	    if(monDir == null || !monDir.isFolder()) 
		throw new FileNotFoundException();
	}

	if(debug) 
	    log("monitor directory is " + monDir.getName());// NOI18N

	// Current directory

	if(currDir == null || !currDir.isFolder()) {

	    try {
		currDir = monDir.getFileObject(currDirStr);
	    }
	    catch(Exception ex) { }
	    
	    if(currDir == null || !currDir.isFolder()) {
		lock = null;
		if(currDir != null) {
		    try {
			lock = currDir.lock();
			currDir.delete(lock);
		    }
		    catch(FileAlreadyLockedException falex) {
			throw new FileNotFoundException();
		    }
		    catch(IOException ex) {
			throw new FileNotFoundException();
		    }
		    finally { 
			if(lock != null) lock.releaseLock();
		    }
		}
		try {
		    currDir = monDir.createFolder(currDirStr);
		}
		catch(IOException ex) {
		    if(debug) ex.printStackTrace();
		}
	    }
	    if(currDir == null || !currDir.isFolder()) 
		throw new FileNotFoundException();
	}
	
	if(debug) log("curr directory is " + currDir.getName()); // NOI18N

	// Save Directory
	if(saveDir == null || !saveDir.isFolder()) {
	    try {
		saveDir = monDir.getFileObject(saveDirStr);
	    }
	    catch(Exception ex) { }
	    
	    if(saveDir == null || !saveDir.isFolder()) {
		if(saveDir != null) {
		    lock = null;
		    try {
			lock = saveDir.lock();
			saveDir.delete(lock);
		    }
		    catch(FileAlreadyLockedException falex) {
			throw new FileNotFoundException();
		    }
		    catch(IOException ex) {
			throw new FileNotFoundException();
		    }
		    finally { 
			if(lock != null) lock.releaseLock();
		    }
		}
		try {
		    saveDir = monDir.createFolder(saveDirStr);
		}
		catch(IOException ex) {
		    if(debug) ex.printStackTrace();
		}
	    }
	    if(saveDir == null || !saveDir.isFolder()) 
		throw new FileNotFoundException();

	    if(debug) 
		log("save directory is " + saveDir.getName()); // NOI18N
	}

	// Replay Directory

	if(replayDir == null || !replayDir.isFolder()) {

	    try {
		replayDir = monDir.getFileObject(replayDirStr);
	    }
	    catch(Exception ex) { }
	    
	    if(replayDir == null || !replayDir.isFolder()) {
		if(replayDir != null) {
		    lock = null;
		    try {
			lock = replayDir.lock();
			replayDir.delete(lock);
		    }
		    catch(FileAlreadyLockedException falex) {
			throw new FileNotFoundException();
		    }
		    catch(IOException ex) {
			throw new FileNotFoundException();
		    }
		    finally { 
			if(lock != null) lock.releaseLock();
		    }
		}
		try {
		    replayDir = monDir.createFolder(replayDirStr);
		}
		catch(Exception ex) {
		    if(debug) ex.printStackTrace();
		}
	    }
	    if(replayDir == null || !replayDir.isFolder()) 
		throw new FileNotFoundException();

	    if(debug) 
		log("replay directory is " + replayDir.getName());// NOI18N
	}
    }