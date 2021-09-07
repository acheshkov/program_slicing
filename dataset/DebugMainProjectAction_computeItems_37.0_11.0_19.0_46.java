private void computeItems() {
            if (menu == null) {
                return ;
            }
            boolean wasSeparator = items.length > 0;
            for (int i = 0; i < items.length; i++) {
                menu.remove(items[i]);
            }
            synchronized (debugItems) {
                if (debugItems.isEmpty()) {
                    items = new JMenuItem[0];
                } else {
                    int n = debugItems.size();
                    items = new JMenuItem[n];
                    int i, j;
                    for (i = j = 0; i < n; i++) {
                        DebugActionItem dai = debugItems.get(i);
                        String dispName = dai.getDisplayName();
                        if (Objects.equals(selectedProjectRoot, dai.getRoot())) {
                            continue;
                        }
                        items[j] = new JMenuItem(dispName);
                        items[j].putClientProperty(DEBUG_ACTION_ITEM_PROP_NAME, dai.getActionItem());
                        items[j].addActionListener(this);
                        j++;
                    }
                    if (j < items.length) {
                        items = Arrays.copyOf(items, j);
                    }
                }
            }
            if (items.length == 0) {
                if (wasSeparator) {
                    menu.remove(separator1);
                    menu.remove(separator2);
                }
            } else {
                if (!wasSeparator) {
                    menu.insert(separator1, 1);
                }
                int i;
                for (i = 0; i < items.length; i++) {
                    menu.insert(items[i], i + 2);
                }
                menu.insert(separator2, i + 2);
            }
        }