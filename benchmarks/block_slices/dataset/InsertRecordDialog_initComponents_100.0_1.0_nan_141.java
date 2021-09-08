@SuppressWarnings("unchecked") // NOI18N
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        jTextArea1 = new javax.swing.JTextArea();
        jSplitPane1 = new javax.swing.JSplitPane();
        jScrollPane1 = new javax.swing.JScrollPane();
        jPanel3 = new javax.swing.JPanel();
        jScrollPane2 = new javax.swing.JScrollPane();
        jEditorPane1 = new javax.swing.JEditorPane();
        btnPanel = new javax.swing.JPanel();
        previewBtn = new javax.swing.JButton();
        addBtn = new javax.swing.JButton();
        removeBtn = new javax.swing.JButton();
        executeBtn = new javax.swing.JButton();
        cancelBtn = new javax.swing.JButton();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.title")); // NOI18N
        setBackground(java.awt.Color.white);
        setFont(new java.awt.Font("Dialog", 0, 12));
        setForeground(java.awt.Color.black);
        setLocationByPlatform(true);
        setModal(true);

        jTextArea1.setBackground(javax.swing.UIManager.getDefaults().getColor("Label.background"));
        jTextArea1.setColumns(20);
        jTextArea1.setEditable(false);
        jTextArea1.setFont(jTextArea1.getFont());
        jTextArea1.setLineWrap(true);
        jTextArea1.setRows(3);
        jTextArea1.setText(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.jTextArea1.text")); // NOI18N
        jTextArea1.setWrapStyleWord(true);
        jTextArea1.setBorder(javax.swing.BorderFactory.createEmptyBorder(10, 10, 10, 10));
        getContentPane().add(jTextArea1, java.awt.BorderLayout.NORTH);
        jTextArea1.getAccessibleContext().setAccessibleName(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "insertRecodrDialog.jTextArea")); // NOI18N
        jTextArea1.getAccessibleContext().setAccessibleDescription(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "insertRecord.textarea.desc")); // NOI18N

        jSplitPane1.setDividerLocation(250);
        jSplitPane1.setOrientation(javax.swing.JSplitPane.VERTICAL_SPLIT);
        jSplitPane1.setLastDividerLocation(250);
        jSplitPane1.setRequestFocusEnabled(false);

        jScrollPane1.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(204, 204, 255)));
        jScrollPane1.setFont(jScrollPane1.getFont());

        jPanel3.setBorder(javax.swing.BorderFactory.createEmptyBorder(5, 5, 5, 5));
        jPanel3.setForeground(new java.awt.Color(204, 204, 255));
        jPanel3.setFont(jPanel3.getFont().deriveFont(jPanel3.getFont().getSize()+1f));
        jPanel3.setLayout(new java.awt.GridBagLayout());
        jScrollPane1.setViewportView(jPanel3);

        jSplitPane1.setTopComponent(jScrollPane1);

        jScrollPane2.setFont(jScrollPane2.getFont());

        jEditorPane1.setEditable(false);
        jEditorPane1.setEditorKit(CloneableEditorSupport.getEditorKit("text/x-sql"));
        jEditorPane1.setToolTipText(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.jEditorPane1.toolTipText")); // NOI18N
        jEditorPane1.setOpaque(false);
        jScrollPane2.setViewportView(jEditorPane1);

        jSplitPane1.setBottomComponent(jScrollPane2);

        getContentPane().add(jSplitPane1, java.awt.BorderLayout.CENTER);

        btnPanel.setBorder(javax.swing.BorderFactory.createEmptyBorder(1, 1, 20, 10));
        btnPanel.setFont(btnPanel.getFont());
        btnPanel.setPreferredSize(new java.awt.Dimension(550, 50));
        btnPanel.setLayout(new java.awt.FlowLayout(java.awt.FlowLayout.RIGHT));

        previewBtn.setFont(previewBtn.getFont());
        previewBtn.setMnemonic('S');
        org.openide.awt.Mnemonics.setLocalizedText(previewBtn, org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.previewBtn.text")); // NOI18N
        previewBtn.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                previewBtnActionPerformed(evt);
            }
        });
        btnPanel.add(previewBtn);
        previewBtn.getAccessibleContext().setAccessibleName(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.previewBtn.text")); // NOI18N
        previewBtn.getAccessibleContext().setAccessibleDescription(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.previewBtn.text")); // NOI18N

        org.openide.awt.Mnemonics.setLocalizedText(addBtn, org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.addBtn.text_1")); // NOI18N
        addBtn.setToolTipText(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.addBtn.toolTipText")); // NOI18N
        addBtn.setMaximumSize(previewBtn.getMaximumSize());
        addBtn.setMinimumSize(previewBtn.getMinimumSize());
        addBtn.setPreferredSize(previewBtn.getPreferredSize());
        addBtn.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                addBtnActionPerformed(evt);
            }
        });
        btnPanel.add(addBtn);

        org.openide.awt.Mnemonics.setLocalizedText(removeBtn, org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.removeBtn.text_1")); // NOI18N
        removeBtn.setToolTipText(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.removeBtn.toolTipText")); // NOI18N
        removeBtn.setEnabled(false);
        removeBtn.setMaximumSize(previewBtn.getMaximumSize());
        removeBtn.setMinimumSize(previewBtn.getMinimumSize());
        removeBtn.setPreferredSize(previewBtn.getPreferredSize());
        removeBtn.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                removeBtnActionPerformed(evt);
            }
        });
        btnPanel.add(removeBtn);

        executeBtn.setFont(executeBtn.getFont());
        org.openide.awt.Mnemonics.setLocalizedText(executeBtn, org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.executeBtn.text")); // NOI18N
        executeBtn.setMaximumSize(previewBtn.getMaximumSize());
        executeBtn.setMinimumSize(previewBtn.getMinimumSize());
        executeBtn.setPreferredSize(previewBtn.getPreferredSize());
        executeBtn.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                executeBtnActionPerformed(evt);
            }
        });
        btnPanel.add(executeBtn);
        executeBtn.getAccessibleContext().setAccessibleName(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.executeBtn.text")); // NOI18N
        executeBtn.getAccessibleContext().setAccessibleDescription(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.executeBtn.text")); // NOI18N

        cancelBtn.setFont(cancelBtn.getFont());
        org.openide.awt.Mnemonics.setLocalizedText(cancelBtn, org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.cancelBtn.text")); // NOI18N
        cancelBtn.setMaximumSize(previewBtn.getMaximumSize());
        cancelBtn.setMinimumSize(previewBtn.getMinimumSize());
        cancelBtn.setPreferredSize(previewBtn.getPreferredSize());
        cancelBtn.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                cancelBtnActionPerformed(evt);
            }
        });
        btnPanel.add(cancelBtn);
        cancelBtn.getAccessibleContext().setAccessibleName(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.cancelBtn.text")); // NOI18N
        cancelBtn.getAccessibleContext().setAccessibleDescription(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.cancelBtn.text")); // NOI18N

        getContentPane().add(btnPanel, java.awt.BorderLayout.SOUTH);

        getAccessibleContext().setAccessibleName(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.AccessibleContext.accessibleName")); // NOI18N
        getAccessibleContext().setAccessibleDescription(org.openide.util.NbBundle.getMessage(InsertRecordDialog.class, "InsertRecordDialog.AccessibleContext.accessibleDescription")); // NOI18N
        getAccessibleContext().setAccessibleParent(null);
    }