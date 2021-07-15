	protected void initializeApplicationSection(ILaunchConfiguration config) throws CoreException {

		String attribute = getApplicationAttribute();

		// first see if the application name has been set on the launch config
		String application = config.getAttribute(attribute, (String) null);
		if (application == null || fApplicationCombo.indexOf(application) == -1) {
			application = null;

			// check if the user has entered the -application arg in the program arg field
			StringTokenizer tokenizer = new StringTokenizer(config.getAttribute(IJavaLaunchConfigurationConstants.ATTR_PROGRAM_ARGUMENTS, "")); //$NON-NLS-1$
			while (tokenizer.hasMoreTokens()) {
				String token = tokenizer.nextToken();
				if (token.equals("-application") && tokenizer.hasMoreTokens()) { //$NON-NLS-1$
					application = tokenizer.nextToken();
					break;
				}
			}

			int index = -1;
			if (application != null)
				index = fApplicationCombo.indexOf(application);

			// use default application as specified in the install.ini of the target platform
			if (index == -1)
				index = fApplicationCombo.indexOf(TargetPlatform.getDefaultApplication());

			if (index != -1) {
				fApplicationCombo.setText(fApplicationCombo.getItem(index));
			} else if (fApplicationCombo.getItemCount() > 0) {
				fApplicationCombo.setText(fApplicationCombo.getItem(0));
			}
		} else {
			fApplicationCombo.setText(application);
		}
	}