private boolean handleStatus(SynchronizeQueryCommand cmd, boolean handleExceptions) throws CoreException {
        IStatus status = cmd.getStatus();
        if(status == null || status.isOK()) {
            return false;
        }
        Bugzilla.LOG.log(Level.FINE, "command {0} returned status : {1}", new Object[] {cmd, status.getMessage()}); // NOI18N

        if (status.getException() instanceof CoreException) {
            throw (CoreException) status.getException();
        }

        boolean isHtml = false;
        String errMsg = null;
        if(status instanceof RepositoryStatus) {
            RepositoryStatus rstatus = (RepositoryStatus) status;
            errMsg = rstatus.getHtmlMessage();
            isHtml = errMsg != null;
        }
        if(errMsg == null) {
            errMsg = status.getMessage();
        }
        cmd.setErrorMessage(errMsg);
        cmd.setFailed(true);

        if(!handleExceptions) {
            return true;
        }

        BugzillaConfiguration conf = repository.getConfiguration();
        if(conf.isValid()) {
            BugzillaVersion version = conf.getInstalledVersion();
            if(version.compareMajorMinorOnly(BugzillaAutoupdate.SUPPORTED_BUGZILLA_VERSION) > 0) {
                notifyErrorMessage(
                        NbBundle.getMessage(BugzillaExecutor.class, "MSG_BUGZILLA_ERROR_WARNING", status.getMessage()) + "\n\n" + 
                        NbBundle.getMessage(BugzillaExecutor.class, "MSG_BUGZILLA_VERSION_WARNING1", version) + "\n" +          // NOI18N
                        (true ? NbBundle.getMessage(BugzillaExecutor.class, "MSG_BUGZILLA_VERSION_WARNING2") : ""));        // NOI18N
                return true;
            }
        }
        if(isHtml) {
            notifyHtmlMessage(errMsg, repository, true);
        } else {
            notifyErrorMessage(NbBundle.getMessage(BugzillaExecutor.class, "MSG_BUGZILLA_ERROR_WARNING", errMsg)); // NOI18N
        }
        return true;
    }