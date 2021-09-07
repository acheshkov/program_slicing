private void fileOutput() throws IOException, FileStateInvalidException, TransformerException {
            OutputStream outputStream = null;
            FileLock fileLock = null;

            try {
                fileLock = resultFO.lock();
                outputStream = resultFO.getOutputStream(fileLock);
                
                Result outputResult = new StreamResult(outputStream); // throws IOException, FileStateInvalidException
                
//                if ( Util.THIS.isLoggable() ) /* then */ {
//                    Util.THIS.debug("    resultFO = " + resultFO);
//                    Util.THIS.debug("    outputResult = " + outputResult);
//                }
                String xmlName = data.getInput();
                String xslName = data.getXSL();
                TransformPerformer.this.getCookieObserver().message(NbBundle.getMessage(TransformPerformer.class, "MSG_transformation_1", xmlName, xslName));
                TransformUtil.transform(xmlSource, transformableCookie, xslSource, outputResult, TransformPerformer.this.getCookieObserver()); // throws TransformerException
                // #186348  - should unlock first, then revalidate DO
            } catch (FileAlreadyLockedException exc) {
                throw (FileAlreadyLockedException) ErrorManager.getDefault().annotate(exc, NbBundle.getMessage(TransformPerformer.class, "ERR_FileAlreadyLockedException_output"));
            } finally {
                try {
                    if ( outputStream != null ) {
                        outputStream.close();
                    }
                } catch (IOException ex) {
                    // ignore, but log:
                    ErrorManager.getDefault().log(ErrorManager.INFORMATIONAL, "Could not close output stream for: " + resultFO);
                }
                if ( fileLock != null ) {
                    fileLock.releaseLock();
                }
            }
            // revalidate DataObject associated with possibly partially written file #28079
            try {
                DataObject dataObject = DataObject.find(resultFO);
                dataObject.setValid(false);
            } catch (DataObjectNotFoundException dnf) {
                throw new IllegalStateException();
            } catch (PropertyVetoException pve) {
                ErrorManager.getDefault().log(ErrorManager.INFORMATIONAL, "Cannot invalidate " + resultFO);
            }
            // vlv # 103384
            if ( data.getProcessOutput() == TransformHistory.APPLY_DEFAULT_ACTION ) {
                GuiUtil.performDefaultAction(resultFO);
            } else if ( data.getProcessOutput() == TransformHistory.OPEN_IN_BROWSER ) {
                showURL(resultFO.getURL());
            }
        }