@Override
    public boolean dispatchKeyEvent(KeyEvent e)
    {
        if (e.getID() == KeyEvent.KEY_TYPED)
            return false;

        /*
         * When the UI uses a single window and we do not have a callContainer,
         * we do not seem to be able to deal with the situation.
         */
        if ((GuiActivator.getUIService().getSingleWindowContainer() != null)
                && ((callContainer == null) || !callContainer.isFocusOwner()))
            return false;

        boolean dispatch = false;

        synchronized (parents)
        {
            for (int i = 0, count = parents.size(); i < count; i++)
            {
                if (parents.get(i).isFocused())
                {
                    dispatch = true;
                    break;
                }
            }
        }

        // If we are not focused, the KeyEvent was not meant for us.
        if (dispatch)
        {
            for (int i = 0; i < AVAILABLE_TONES.length; i++)
            {
                DTMFToneInfo info = AVAILABLE_TONES[i];

                if (info.keyChar == e.getKeyChar())
                {
                    switch (e.getID())
                    {
                    case KeyEvent.KEY_PRESSED:
                        startSendingDtmfTone(info);
                        break;
                    case KeyEvent.KEY_RELEASED:
                        stopSendingDtmfTone();
                        break;
                    }
                    break;
                }
            }
        }

        return false;
    }