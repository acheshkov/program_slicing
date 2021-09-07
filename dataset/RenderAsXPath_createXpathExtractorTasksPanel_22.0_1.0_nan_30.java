private JPanel createXpathExtractorTasksPanel() {
        Box xpathActionPanel = Box.createVerticalBox();

        Box selectorAndButton = Box.createHorizontalBox();

        Border margin = new EmptyBorder(5, 5, 0, 5);
        xpathActionPanel.setBorder(margin);
        xpathExpressionField = new JLabeledTextField(JMeterUtils.getResString("xpath_tester_field")); // $NON-NLS-1$

        JButton xpathTester = new JButton(JMeterUtils.getResString("xpath_tester_button_test")); // $NON-NLS-1$
        xpathTester.setActionCommand(XPATH_TESTER_COMMAND);
        xpathTester.addActionListener(this);

        selectorAndButton.add(xpathExpressionField);
        selectorAndButton.add(xpathTester);

        xpathActionPanel.add(selectorAndButton);
        xpathActionPanel.add(xmlConfPanel);
        xpathActionPanel.add(getFragment);

        xpathResultField = new JTextArea();
        xpathResultField.setEditable(false);
        xpathResultField.setLineWrap(true);
        xpathResultField.setWrapStyleWord(true);

        JPanel xpathTasksPanel = new JPanel(new BorderLayout(0, 5));
        xpathTasksPanel.add(xpathActionPanel, BorderLayout.NORTH);
        xpathTasksPanel.add(GuiUtils.makeScrollPane(xpathResultField), BorderLayout.CENTER);

        return xpathTasksPanel;
    }