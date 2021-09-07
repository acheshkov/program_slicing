@Override
    public void run() {
      try {
        if (isRemove) {
          downloader.remove();
        } else {
          int errorCount = 0;
          long errorPosition = C.LENGTH_UNSET;
          while (!isCanceled) {
            try {
              downloader.download(/* progressListener= */ this);
              break;
            } catch (IOException e) {
              if (!isCanceled) {
                long bytesDownloaded = downloadProgress.bytesDownloaded;
                if (bytesDownloaded != errorPosition) {
                  errorPosition = bytesDownloaded;
                  errorCount = 0;
                }
                if (++errorCount > minRetryCount) {
                  throw e;
                }
                Thread.sleep(getRetryDelayMillis(errorCount));
              }
            }
          }
        }
      } catch (Throwable e) {
        finalError = e;
      }
      @Nullable Handler internalHandler = this.internalHandler;
      if (internalHandler != null) {
        internalHandler.obtainMessage(MSG_TASK_STOPPED, this).sendToTarget();
      }
    }