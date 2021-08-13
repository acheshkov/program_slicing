	protected void internalInitialize() throws StorageException {
		if (cipherAlgorithm != null && keyFactoryAlgorithm != null) {
			if (roundtrip(cipherAlgorithm, keyFactoryAlgorithm))
				return;
			// this is a bad situation - JVM cipher no longer available. Both log and throw an exception
			String msg = NLS.bind(SecAuthMessages.noAlgorithm, cipherAlgorithm);
			StorageException e = new StorageException(StorageException.INTERNAL_ERROR, msg);
			AuthPlugin.getDefault().logError(msg, e);
			throw e;
		}
		if (cipherAlgorithm == null || keyFactoryAlgorithm == null) {
			IEclipsePreferences eclipseNode = new ConfigurationScope().getNode(AuthPlugin.PI_AUTH);
			cipherAlgorithm = eclipseNode.get(IStorageConstants.CIPHER_KEY, IStorageConstants.DEFAULT_CIPHER);
			keyFactoryAlgorithm = eclipseNode.get(IStorageConstants.KEY_FACTORY_KEY, IStorageConstants.DEFAULT_KEY_FACTORY);
		}
		if (roundtrip(cipherAlgorithm, keyFactoryAlgorithm))
			return;
		String unavailableCipher = cipherAlgorithm;

		detect();
		if (availableCiphers.size() == 0)
			throw new StorageException(StorageException.INTERNAL_ERROR, SecAuthMessages.noAlgorithms);

		// use first available
		cipherAlgorithm = (String) availableCiphers.keySet().iterator().next();
		keyFactoryAlgorithm = (String) availableCiphers.get(cipherAlgorithm);

		String msg = NLS.bind(SecAuthMessages.usingAlgorithm, unavailableCipher, cipherAlgorithm);
		AuthPlugin.getDefault().logMessage(msg);
	}