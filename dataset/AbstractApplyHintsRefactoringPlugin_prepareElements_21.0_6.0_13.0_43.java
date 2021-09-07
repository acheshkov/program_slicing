protected final void prepareElements(BatchResult candidates, ProgressHandleWrapper w, final RefactoringElementsBag refactoringElements, final boolean verify, List<MessageImpl> problems) {
        final Map<FileObject, Collection<RefactoringElementImplementation>> file2Changes = new TreeMap<FileObject, Collection<RefactoringElementImplementation>>(FILE_COMPARATOR);
        if (verify) {
            BatchSearch.getVerifiedSpans(candidates, w, new BatchSearch.VerifiedSpansCallBack() {
                public void groupStarted() {}
                public boolean spansVerified(CompilationController wc, Resource r, Collection<? extends ErrorDescription> hints) throws Exception {
                    List<PositionBounds> spans = new LinkedList<PositionBounds>();

                    for (ErrorDescription ed : hints) {
                        spans.add(ed.getRange());
                    }
                    
                    file2Changes.put(r.getResolvedFile(), Utilities.createRefactoringElementImplementation(r.getResolvedFile(), spans, verify));
                    return true;
                }
                public void groupFinished() {}
                public void cannotVerifySpan(Resource r) {
                    file2Changes.put(r.getResolvedFile(), Utilities.createRefactoringElementImplementation(r.getResolvedFile(), prepareSpansFor(r), verify));
                }
            }, problems, cancel);
        } else {
            int[] parts = new int[candidates.getResources().size()];
            int   index = 0;

            for (Collection<? extends Resource> resources : candidates.getResources()) {
                parts[index++] = resources.size();
            }

            ProgressHandleWrapper inner = w.startNextPartWithEmbedding(parts);

            for (Collection<? extends Resource> it :candidates.getResources()) {
                inner.startNextPart(it.size());

                for (Resource r : it) {
                    file2Changes.put(r.getResolvedFile(), Utilities.createRefactoringElementImplementation(r.getResolvedFile(), prepareSpansFor(r), verify));
                    inner.tick();
                }
            }
        }
        
        for (Collection<RefactoringElementImplementation> res : file2Changes.values()) {
            refactoringElements.addAll(refactoring, res);
        }
    }