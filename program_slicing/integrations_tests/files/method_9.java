	private void autoDetectRoot(IPath path) throws CoreException {
		if (!fRootDetected) {
			ZipFile zip = null;
			try {
				zip = getArchive();
			} catch (IOException e) {
				throw new CoreException(new Status(IStatus.ERROR, LaunchingPlugin.getUniqueIdentifier(), IJavaLaunchConfigurationConstants.ERR_INTERNAL_ERROR, 
					NLS.bind(LaunchingMessages.ArchiveSourceLocation_Exception_occurred_while_detecting_root_source_directory_in_archive__0__1, new String[] {getName()}), e)); 
			}
			synchronized (zip) {
				Enumeration<? extends ZipEntry> entries = zip.entries();
				String fileName = path.toString();
				try {
					while (entries.hasMoreElements()) {
						ZipEntry entry = entries.nextElement();
						String entryName = entry.getName();
						if (entryName.endsWith(fileName)) {
							int rootLength = entryName.length() - fileName.length();
							if (rootLength > 0) {
								String root = entryName.substring(0, rootLength);
								setRootPath(root);
							}
							fRootDetected = true;
							return;
						}
					}
				} catch (IllegalStateException e) {
					throw new CoreException(new Status(IStatus.ERROR, LaunchingPlugin.getUniqueIdentifier(), IJavaLaunchConfigurationConstants.ERR_INTERNAL_ERROR, 
						NLS.bind(LaunchingMessages.ArchiveSourceLocation_Exception_occurred_while_detecting_root_source_directory_in_archive__0__2, new String[] {getName()}), e)); 
				}
			}
		}
	}