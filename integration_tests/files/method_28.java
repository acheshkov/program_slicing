    public boolean loadEntryByID(String id, boolean activate,
            boolean onlyLoadOnce, Object datasource) {
        if (id == null) {
            return false;
        }
        MdiEntry entry = getEntry(id);
        if (entry != null) {
            if (datasource != null) {
                entry.setDatasource(datasource);
            }
            if (activate) {
                showEntry(entry);
            }
            return true;
        }

        @SuppressWarnings("deprecation")
        boolean loadedOnce = COConfigurationManager.getBooleanParameter("sb.once."
                + id, false);
        if (loadedOnce && onlyLoadOnce) {
            return false;
        }

        if (id.equals(SIDEBAR_SECTION_WELCOME)) {
            SideBarEntrySWT entryWelcome = (SideBarEntrySWT) createWelcomeSection();
            if (activate) {
                showEntry(entryWelcome);
            }
            return true;
        } else if (id.startsWith("ContentNetwork.")) {
            long networkID = Long.parseLong(id.substring(15));
            handleContentNetworkSwitch(id, networkID);
            return true;
        } else if (id.equals("library") || id.equals("minilibrary")) {
            id = SIDEBAR_SECTION_LIBRARY;
            loadEntryByID(id, activate);
            return true;
        } else if (id.equals("activities")) {
            id = SIDEBAR_SECTION_ACTIVITIES;
            loadEntryByID(id, activate);
            return true;
        }

        MdiEntryCreationListener mdiEntryCreationListener = mapIdToCreationListener.get(id);
        if (mdiEntryCreationListener != null) {
            MdiEntry mdiEntry = mdiEntryCreationListener.createMDiEntry(id);
            if (datasource != null) {
                mdiEntry.setDatasource(datasource);
            }
            if (mdiEntry instanceof SideBarEntrySWT) {
                if (onlyLoadOnce) {
                    COConfigurationManager.setParameter("sb.once." + id, true);
                }
                if (activate) {
                    showEntry(mdiEntry);
                }
                return true;
            }
        } else {
            setEntryAutoOpen(id, datasource, true);
        }

        return false;
    }