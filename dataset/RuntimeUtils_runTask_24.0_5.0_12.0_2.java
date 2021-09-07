public static boolean runTask(final DBRRunnableWithProgress task, String taskName, final long waitTime) {
        return runTask(task, taskName, waitTime, false);
    }