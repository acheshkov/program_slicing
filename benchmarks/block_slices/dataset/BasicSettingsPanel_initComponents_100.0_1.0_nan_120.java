private void initComponents() {
        java.awt.GridBagConstraints gridBagConstraints;

        lblMode = new javax.swing.JLabel();
        comMode = new javax.swing.JComboBox();
        cbOpenedOnStart = new javax.swing.JCheckBox();
        cbKeepPrefSize = new javax.swing.JCheckBox();
        cbSlidingNotAllowed = new javax.swing.JCheckBox();
        cbClosingNotAllowed = new javax.swing.JCheckBox();
        cbUndockingNotAllowed = new javax.swing.JCheckBox();
        cbDraggingNotAllowed = new javax.swing.JCheckBox();
        cbMaximizationNotAllowed = new javax.swing.JCheckBox();
        redefine = new javax.swing.JButton();

        setLayout(new java.awt.GridBagLayout());

        lblMode.setLabelFor(comMode);
        org.openide.awt.Mnemonics.setLocalizedText(lblMode, org.openide.util.NbBundle.getMessage(BasicSettingsPanel.class, "LBL_Mode")); // NOI18N
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.anchor = java.awt.GridBagConstraints.WEST;
        gridBagConstraints.insets = new java.awt.Insets(12, 6, 0, 0);
        add(lblMode, gridBagConstraints);

        comMode.addItemListener(new java.awt.event.ItemListener() {
            public void itemStateChanged(java.awt.event.ItemEvent evt) {
                windowPosChanged(evt);
            }
        });
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.NORTHWEST;
        gridBagConstraints.weightx = 0.1;
        gridBagConstraints.insets = new java.awt.Insets(12, 6, 0, 6);
        add(comMode, gridBagConstraints);

        org.openide.awt.Mnemonics.setLocalizedText(cbOpenedOnStart, org.openide.util.NbBundle.getMessage(BasicSettingsPanel.class, "LBL_OpenOnStart")); // NOI18N
        cbOpenedOnStart.setBorder(javax.swing.BorderFactory.createEmptyBorder(0, 0, 0, 0));
        cbOpenedOnStart.setMargin(new java.awt.Insets(0, 0, 0, 0));
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridx = 0;
        gridBagConstraints.gridy = 1;
        gridBagConstraints.gridwidth = 2;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.NORTHWEST;
        gridBagConstraints.insets = new java.awt.Insets(12, 6, 0, 0);
        add(cbOpenedOnStart, gridBagConstraints);

        org.openide.awt.Mnemonics.setLocalizedText(cbKeepPrefSize, org.openide.util.NbBundle.getMessage(BasicSettingsPanel.class, "LBL_KeepPrefSize")); // NOI18N
        cbKeepPrefSize.setBorder(javax.swing.BorderFactory.createEmptyBorder(0, 0, 0, 0));
        cbKeepPrefSize.setEnabled(false);
        cbKeepPrefSize.setMargin(new java.awt.Insets(0, 0, 0, 0));
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridx = 0;
        gridBagConstraints.gridy = 2;
        gridBagConstraints.gridwidth = 2;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.NORTHWEST;
        gridBagConstraints.insets = new java.awt.Insets(12, 6, 0, 0);
        add(cbKeepPrefSize, gridBagConstraints);

        org.openide.awt.Mnemonics.setLocalizedText(cbSlidingNotAllowed, org.openide.util.NbBundle.getMessage(BasicSettingsPanel.class, "CTL_SlidingNotAllowed")); // NOI18N
        cbSlidingNotAllowed.setBorder(javax.swing.BorderFactory.createEmptyBorder(0, 0, 0, 0));
        cbSlidingNotAllowed.setEnabled(false);
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridx = 0;
        gridBagConstraints.gridy = 3;
        gridBagConstraints.gridwidth = 2;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.NORTHWEST;
        gridBagConstraints.insets = new java.awt.Insets(12, 6, 0, 0);
        add(cbSlidingNotAllowed, gridBagConstraints);

        org.openide.awt.Mnemonics.setLocalizedText(cbClosingNotAllowed, org.openide.util.NbBundle.getMessage(BasicSettingsPanel.class, "CTL_ClosingNotAllowed")); // NOI18N
        cbClosingNotAllowed.setBorder(javax.swing.BorderFactory.createEmptyBorder(0, 0, 0, 0));
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridx = 0;
        gridBagConstraints.gridy = 4;
        gridBagConstraints.gridwidth = 2;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.NORTHWEST;
        gridBagConstraints.insets = new java.awt.Insets(12, 6, 0, 0);
        add(cbClosingNotAllowed, gridBagConstraints);

        org.openide.awt.Mnemonics.setLocalizedText(cbUndockingNotAllowed, org.openide.util.NbBundle.getMessage(BasicSettingsPanel.class, "CTL_UndockingNotAllowed")); // NOI18N
        cbUndockingNotAllowed.setBorder(javax.swing.BorderFactory.createEmptyBorder(0, 0, 0, 0));
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridx = 0;
        gridBagConstraints.gridy = 5;
        gridBagConstraints.gridwidth = 2;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.NORTHWEST;
        gridBagConstraints.insets = new java.awt.Insets(12, 6, 0, 0);
        add(cbUndockingNotAllowed, gridBagConstraints);

        org.openide.awt.Mnemonics.setLocalizedText(cbDraggingNotAllowed, org.openide.util.NbBundle.getMessage(BasicSettingsPanel.class, "CTL_DraggingNotAllowed")); // NOI18N
        cbDraggingNotAllowed.setBorder(javax.swing.BorderFactory.createEmptyBorder(0, 0, 0, 0));
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridx = 0;
        gridBagConstraints.gridy = 6;
        gridBagConstraints.gridwidth = 2;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.NORTHWEST;
        gridBagConstraints.insets = new java.awt.Insets(12, 6, 0, 0);
        add(cbDraggingNotAllowed, gridBagConstraints);

        org.openide.awt.Mnemonics.setLocalizedText(cbMaximizationNotAllowed, org.openide.util.NbBundle.getMessage(BasicSettingsPanel.class, "CTL_MaximizationNotAllowed")); // NOI18N
        cbMaximizationNotAllowed.setBorder(javax.swing.BorderFactory.createEmptyBorder(0, 0, 0, 0));
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridx = 0;
        gridBagConstraints.gridy = 7;
        gridBagConstraints.gridwidth = 2;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.NORTHWEST;
        gridBagConstraints.weighty = 0.1;
        gridBagConstraints.insets = new java.awt.Insets(12, 6, 0, 0);
        add(cbMaximizationNotAllowed, gridBagConstraints);

        org.openide.awt.Mnemonics.setLocalizedText(redefine, org.openide.util.NbBundle.getMessage(BasicSettingsPanel.class, "LBL_redefine")); // NOI18N
        redefine.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                redefineActionPerformed(evt);
            }
        });
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.anchor = java.awt.GridBagConstraints.PAGE_END;
        gridBagConstraints.insets = new java.awt.Insets(0, 0, 0, 12);
        add(redefine, gridBagConstraints);
    }