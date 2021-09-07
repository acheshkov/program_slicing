public void notify(String message, int status)
    {
        try {
            if (trayItem == null) {
                try {
                    show();
                } catch (Exception e) {
                    log.warn("Can't show tray item", e);
                    return;
                }
            }
            TrayIcon.MessageType type;
            switch (status) {
                case IStatus.INFO: type = TrayIcon.MessageType.INFO; break;
                case IStatus.ERROR: type = TrayIcon.MessageType.ERROR; break;
                case IStatus.WARNING: type = TrayIcon.MessageType.WARNING; break;
                default: type = TrayIcon.MessageType.NONE; break;
            }
            trayItem.displayMessage(GeneralUtils.getProductTitle(), message, type);
        } catch (Throwable e) {
            log.error("Error showing tray notification", e);
        }
    }