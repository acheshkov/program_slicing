    private void loadEquipment(Protomech t, String sName, int nLoc) throws EntityLoadingException {
        String[] saEquip = dataFile.getDataAsString(sName + " Equipment");
        if (saEquip == null) {
            return;
        }

        // prefix is "Clan " or "IS "
        String prefix;
        if (t.getTechLevel() == TechConstants.T_CLAN_TW) {
            prefix = "Clan ";
        } else {
            prefix = "IS ";
        }

        for (String element : saEquip) {
            String equipName = element.trim();

            // ProtoMech Ammo comes in non-standard amounts.
            int ammoIndex = equipName.indexOf("Ammo (");
            int shotsCount = 0;
            if (ammoIndex > 0) {
                // Try to get the number of shots.
                try {
                    String shots = equipName.substring(ammoIndex + 6, equipName.length() - 1);
                    shotsCount = Integer.parseInt(shots);
                    if (shotsCount < 0) {
                        throw new EntityLoadingException("Invalid number of shots in: " + equipName + ".");
                    }
                } catch (NumberFormatException badShots) {
                    throw new EntityLoadingException("Could not determine the number of shots in: " + equipName + ".");
                }

                // Strip the shots out of the ammo name.
                equipName = equipName.substring(0, ammoIndex + 4);
            }
            EquipmentType etype = EquipmentType.get(equipName);

            if (etype == null) {
                // try w/ prefix
                etype = EquipmentType.get(prefix + equipName);
            }

            if (etype != null) {
                try {
                    // If this is an Ammo slot, only add
                    // the indicated number of shots.
                    if (ammoIndex > 0) {
                        t.addEquipment(etype, nLoc, false, shotsCount);
                    } else {
                        t.addEquipment(etype, nLoc);
                    }
                } catch (LocationFullException ex) {
                    throw new EntityLoadingException(ex.getMessage());
                }
            }
        }
    }