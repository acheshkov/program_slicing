public static void displayMergeWarning (Map<String, Collection<HgLogMessage>> branchHeads, OutputLogger logger, boolean warnInDialog) {
        boolean mulitpleHeads = false;
        for (Map.Entry<String, Collection<HgLogMessage>> e : branchHeads.entrySet()) {
            if (e.getValue().size() > 1) {
                mulitpleHeads = true;
                break;
            }
        }
        if (!mulitpleHeads) {
            return;
        }
        Action a = logger.getOpenOutputAction();
        if (warnInDialog && a != null && JOptionPane.showConfirmDialog(null, NbBundle.getMessage(MergeAction.class, "MSG_MERGE_NEEDED_BRANCHES"), //NOI18N
                NbBundle.getMessage(MergeAction.class, "TITLE_MERGE_NEEDED_BRANCHES"), //NOI18N
                JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE) == JOptionPane.YES_OPTION) {
            a.actionPerformed(new ActionEvent(MergeAction.class, ActionEvent.ACTION_PERFORMED, null));
        }
        logger.outputInRed(NbBundle.getMessage(MergeAction.class, "MSG_MERGE_WARN_NEEDED_BRANCHES")); //NOI18N
        logger.outputInRed(NbBundle.getMessage(MergeAction.class, "MSG_MERGE_DO_NEEDED_BRANCHES")); //NOI18N
        for (Map.Entry<String, Collection<HgLogMessage>> e : branchHeads.entrySet()) {
            Collection<HgLogMessage> heads = e.getValue();
            if (heads.size() > 1) {
                logger.outputInRed(NbBundle.getMessage(MergeAction.class, "MSG_MERGE_WARN_NEEDED_IN_BRANCH", e.getKey())); //NOI18N
                for (HgLogMessage head : heads) {
                    HgUtils.logHgLog(head, logger);
                }
            }
        }
    }