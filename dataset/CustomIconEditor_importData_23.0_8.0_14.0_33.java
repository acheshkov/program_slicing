@Override
        public boolean importData(JComponent comp, Transferable t) {
            if (!t.isDataFlavorSupported(DataFlavor.javaFileListFlavor)) {
                return false;
            }
            List files = null;
            try {
                files = (List) t.getTransferData(DataFlavor.javaFileListFlavor);
            } catch (Exception ex) {
                ErrorManager.getDefault().notify(ErrorManager.INFORMATIONAL, ex);
                return false;
            }

            if (files.size() > 0) {
                File file = (File) files.get(0);
                if (file != null && IconEditor.isImageFileName(file.getName())) {
                    if (setExternalAsCPFile(file)) { // the file is on classpath
                        classPathRadio.setSelected(true);
                    } else {
                        selectedExternalFile = file;
                        selectedURL = null;
                        externalRadio.setSelected(true);
                        try {
                            urlField.setText(file.toURI().toURL().toExternalForm());
                        } catch (MalformedURLException ex) {
                            ErrorManager.getDefault().notify(ErrorManager.INFORMATIONAL, ex);
                        }
                    }
                    updateValue();
                    return true;
                }
            }
            return false;
        }