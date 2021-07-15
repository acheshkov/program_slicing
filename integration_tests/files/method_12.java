	protected IApiProblem createExternalDependenciesProblem(HashMap problems, IReferenceDescriptor dependency, String referenceTypeName, IMemberDescriptor referencedMember, int elementType, int flag) {	
		String resource = referenceTypeName;
		String primaryTypeName = referenceTypeName.replace('$', '.');		
		int charStart = -1, charEnd = -1, lineNumber = -1; 
		if (fJavaProject != null) {
			try {
				
				IType type = fJavaProject.findType(primaryTypeName);
				IResource res = Util.getResource(fJavaProject.getProject(), type);
				if(res == null) {
					return null;
				}
				if(!Util.isManifest(res.getProjectRelativePath())) {
					resource = res.getProjectRelativePath().toString();
				}
				else {
					resource = "."; //$NON-NLS-1$
				}
				if (type != null) {
					ISourceRange range = type.getNameRange();
					charStart = range.getOffset();
					charEnd = charStart + range.getLength();
					try {
						IDocument document = Util.getDocument(type.getCompilationUnit());
						lineNumber = document.getLineOfOffset(charStart);
					} catch (BadLocationException e) {
						// ignore
					}			
					catch (CoreException ce) {}
				}
			} catch (JavaModelException e) {}
		}
		String[] msgArgs = new String[] {referenceTypeName, referencedMember.getName(), dependency.getComponent().getId()};
		int kind = 0;
		switch (elementType) {
			case IElementDescriptor.TYPE : {
				kind = IApiProblem.API_USE_SCAN_TYPE_PROBLEM;				
				break;
			}
			case IElementDescriptor.METHOD : {
				kind = IApiProblem.API_USE_SCAN_METHOD_PROBLEM;
				msgArgs[1] = BuilderMessages.BaseApiAnalyzer_Method + ' ' + msgArgs[1];
				if ((dependency.getReferenceKind() & IReference.REF_CONSTRUCTORMETHOD) > 0) {
					msgArgs[1] = BuilderMessages.BaseApiAnalyzer_Constructor + ' ' + msgArgs[1];
				}
				break;
			}
			case IElementDescriptor.FIELD : {
				kind = IApiProblem.API_USE_SCAN_FIELD_PROBLEM;
				break;
			}
			default: break;
		}
		
		int dependencyNameIndex = 2;	// the comma separated list of dependent plugins 
		int problemId = ApiProblemFactory.createProblemId(IApiProblem.CATEGORY_API_USE_SCAN_PROBLEM, elementType, kind, flag);
		String problemKey = referenceTypeName +  problemId;
		IApiProblem similarProblem =  (IApiProblem) problems.get(problemKey);
		if (similarProblem != null) {
			String[] existingMsgArgs = similarProblem.getMessageArguments()[dependencyNameIndex].split(", "); //$NON-NLS-1$
			if (!Arrays.asList(existingMsgArgs).contains(msgArgs[dependencyNameIndex])) {
				msgArgs[dependencyNameIndex] = similarProblem.getMessageArguments()[dependencyNameIndex] + ',' + ' ' + msgArgs[dependencyNameIndex];
			} else {
				return similarProblem;
			}
		}
		IApiProblem problem = ApiProblemFactory.newApiUseScanProblem(
				resource, 
				primaryTypeName, 
				msgArgs, 
				new String[] {IApiMarkerConstants.API_USESCAN_TYPE}, 
				new String[] {primaryTypeName },
				lineNumber,
				charStart,
				charEnd,
				elementType, 
				kind, 
				flag);
		problems.put(problemKey, problem);
		return problem;		
	}