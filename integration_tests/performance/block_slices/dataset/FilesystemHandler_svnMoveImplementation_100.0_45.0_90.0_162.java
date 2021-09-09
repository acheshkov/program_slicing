private void svnMoveImplementation(final File from, final File to) throws IOException {        
        try {
            boolean force = true; // file with local changes must be forced
            SvnClient client = Subversion.getInstance().getClient(false);

            // prepare destination, it must be under Subversion control
            removeInvalidMetadata();

            File parent;
            if (to.isDirectory()) {
                parent = to;
            } else {
                parent = to.getParentFile();
            }

            boolean parentIgnored = false;
            if (parent != null) {
                assert SvnUtils.isManaged(parent) : "Cannot move " + from.getAbsolutePath() + " to " + to.getAbsolutePath() + ", " + parent.getAbsolutePath() + " is not managed";  // NOI18N see implsMove above
                // a direct cache call could, because of the synchrone svnMoveImplementation handling,
                // trigger an reentrant call on FS => we have to check manually
                if (!isVersioned(parent)) {
                    parentIgnored = !addDirectories(parent);
                }
            }

            // perform
            int retryCounter = 6;
            while (true) {
                try {
                    ISVNStatus toStatus = getStatus(client, to);

                    // check the status - if the file isn't in the repository yet ( ADDED | UNVERSIONED )
                    // then it also can't be moved via the svn client
                    ISVNStatus status = getStatus(client, from);

                    // store all from-s children -> they also have to be refreshed in after move
                    List<File> srcChildren = null;
                    SVNUrl url = status != null && status.isCopied() ? getCopiedUrl(client, from) : null;
                    SVNUrl toUrl = toStatus != null ? toStatus.getUrl() : null;
                    try {
                        srcChildren = SvnUtils.listManagedRecursively(from);
                        boolean moved = true;
                        if (status != null 
                                && (status.getTextStatus().equals(SVNStatusKind.ADDED) || status.getTextStatus().equals(SVNStatusKind.REPLACED)) 
                                && (!status.isCopied() || (url != null && url.equals(toUrl)))) {
                            // 1. file is ADDED (new or added) AND is not COPIED (by invoking svn copy)
                            // 2. file is ADDED and COPIED (by invoking svn copy) and target equals the original from the first copy
                            // otherwise svn move should be invoked

                            File temp = from;
                            if (Utilities.isWindows() && from.equals(to) || Utilities.isMac() && from.getPath().equalsIgnoreCase(to.getPath())) {
                                Subversion.LOG.log(Level.FINE, "svnMoveImplementation: magic workaround for filename case change {0} -> {1}", new Object[] { from, to }); //NOI18N
                                temp = FileUtils.generateTemporaryFile(from.getParentFile(), from.getName());
                                Subversion.LOG.log(Level.FINE, "svnMoveImplementation: magic workaround, step 1: {0} -> {1}", new Object[] { from, temp }); //NOI18N
                                client.move(from, temp, force);
                            }
                            
                            // check if the file wasn't just deleted in this session
                            revertDeleted(client, toStatus, to, true);

                            moved = temp.renameTo(to);
                            if (moved) {
                                // indeed just ADDED, not REPLACED
                                if (status.getTextStatus().equals(SVNStatusKind.ADDED)) {
                                    client.revert(temp, true);
                                } else {
                                    client.remove(new File[] { temp }, true);
                                }
                            }
                        } else if (status != null && (status.getTextStatus().equals(SVNStatusKind.UNVERSIONED)
                                || status.getTextStatus().equals(SVNStatusKind.IGNORED))) { // ignored file CAN'T be moved via svn
                            // check if the file wasn't just deleted in this session
                            revertDeleted(client, toStatus, to, true);

                            moved = from.renameTo(to);
                        } else if (parentIgnored) {
                            // parent is ignored so do not add the file
                            moved = from.renameTo(to);
                            client.remove(new File[] { from }, true);
                        } else {
                            SVNUrl repositorySource = SvnUtils.getRepositoryRootUrl(from);
                            SVNUrl repositoryTarget = SvnUtils.getRepositoryRootUrl(parent);
                            if (repositorySource.equals(repositoryTarget)) {
                                // use client.move only for a single repository
                                try {
                                    client.move(from, to, force);
                                } catch (SVNClientException ex) {
                                    if (Utilities.isWindows() && from.equals(to) || Utilities.isMac() && from.getPath().equalsIgnoreCase(to.getPath())) {
                                        Subversion.LOG.log(Level.FINE, "svnMoveImplementation: magic workaround for filename case change {0} -> {1}", new Object[] { from, to }); //NOI18N
                                        File temp = FileUtils.generateTemporaryFile(to.getParentFile(), from.getName());
                                        Subversion.LOG.log(Level.FINE, "svnMoveImplementation: magic workaround, step 1: {0} -> {1}", new Object[] { from, temp }); //NOI18N
                                        client.move(from, temp, force);
                                        Subversion.LOG.log(Level.FINE, "svnMoveImplementation: magic workaround, step 2: {0} -> {1}", new Object[] { temp, to }); //NOI18N
                                        client.move(temp, to, force);
                                        Subversion.LOG.log(Level.FINE, "svnMoveImplementation: magic workaround completed"); //NOI18N
                                    } else {
                                        throw ex;
                                    }
                                }
                            } else {
                                boolean remove = false;
                                if (from.isDirectory()) {
                                    // tree should be moved separately, otherwise the metadata from the source WC will be copied too
                                    moveFolderToDifferentRepository(from, to);
                                    remove = true;
                                } else if (from.renameTo(to)) {
                                    remove = true;
                                } else {
                                    Subversion.LOG.log(Level.WARNING, FilesystemHandler.class.getName()
                                            + ": cannot rename {0} to {1}", new Object[] {from, to});
                                }
                                if (remove) {
                                    client.remove(new File[] {from}, force);
                                    Subversion.LOG.log(Level.FINE, FilesystemHandler.class.getName()
                                            + ": moving between different repositories {0} to {1}", new Object[] {from, to});
                                }
                            }
                        }
                        if (!moved) {
                            Subversion.LOG.log(Level.INFO, "Cannot rename file {0} to {1}", new Object[] {from, to});
                        }
                    } finally {
                        // we moved the files so schedule them a for a refresh
                        // in the following afterMove call
                        synchronized(movedFiles) {
                            if(srcChildren != null) {
                                movedFiles.addAll(srcChildren);
                            }
                        }
                    }
                    break;
                } catch (SVNClientException e) {
                    // svn: Working copy '/tmp/co/svn-prename-19/AnagramGame-pack-rename/src/com/toy/anagrams/ui2' locked
                    if (e.getMessage().endsWith("' locked") && retryCounter > 0) { // NOI18N
                        // XXX HACK AWT- or FS Monitor Thread performs
                        // concurrent operation
                        try {
                            Thread.sleep(107);
                        } catch (InterruptedException ex) {
                            // ignore
                        }
                        retryCounter--;
                        continue;
                    }
                    if (!WorkingCopyAttributesCache.getInstance().isSuppressed(e)) {
                        SvnClientExceptionHandler.notifyException(e, false, false); // log this
                    }
                    IOException ex = new IOException();
                    Exceptions.attachLocalizedMessage(ex, NbBundle.getMessage(FilesystemHandler.class, "MSG_MoveFailed", new Object[] {from, to, e.getLocalizedMessage()})); //NOI18N
                    ex.getCause().initCause(e);
                    throw ex;
                }
            }
        } catch (SVNClientException e) {
            if (!WorkingCopyAttributesCache.getInstance().isSuppressed(e)) {
                SvnClientExceptionHandler.notifyException(e, false, false); // log this
            }
            IOException ex = new IOException();
            Exceptions.attachLocalizedMessage(ex, "Subversion failed to move " + from.getAbsolutePath() + " to: " + to.getAbsolutePath() + "\n" + e.getLocalizedMessage()); // NOI18N
            ex.getCause().initCause(e);
            throw ex;
        }
    }