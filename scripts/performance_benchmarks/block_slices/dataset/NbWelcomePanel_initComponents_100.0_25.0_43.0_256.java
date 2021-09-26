private void initComponents() {
            // textPane /////////////////////////////////////////////////////////////
            textPane = new NbiTextPane();
            
            // textScrollPane /////////////////////////////////////////////////////////////
            textScrollPane = new NbiTextPane();
            textScrollPane.setOpaque(true);
            textScrollPane.setBackground(Color.WHITE);
            
            detailsTextPane = new NbiTextPane();
            detailsTextPane.setOpaque(true);
            detailsTextPane.setBackground(Color.WHITE);
            
            // scrollPane ////////////////////////////////////////////////////
            scrollPane = new NbiScrollPane(textScrollPane);
            scrollPane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED);
            scrollPane.setViewportBorder(new EmptyBorder(new Insets(0, 0, 0, 0)));
            scrollPane.setBorder(new EmptyBorder(new Insets(0, 0, 0, 0)));
            
            // customizeButton //////////////////////////////////////////////////////
            customizeButton = new NbiButton();
            customizeButton.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent event) {
                    customizeButtonPressed();
                }
            });
            
            // installationSizeLabel ////////////////////////////////////////////////
            installationSizeLabel = new NbiLabel();
            
            
            leftImagePanel = new NbiPanel();
            int width = 0;
            int height = 0;
            final String topLeftImage = SystemUtils.resolveString(
                    System.getProperty(
                    WELCOME_PAGE_LEFT_TOP_IMAGE_PROPERTY));
            final String bottomLeftImage = SystemUtils.resolveString(
                    System.getProperty(
                    WELCOME_PAGE_LEFT_BOTTOM_IMAGE_PROPERTY));
            final String backgroundImage = SystemUtils.resolveString(
                    System.getProperty(
                    WELCOME_PAGE_BACKGROUND_IMAGE_PROPERTY));

            /* For Sun's JDK branding
            int bottomAnchor = NbiPanel.ANCHOR_BOTTOM_LEFT;
            if(type.isJDKBundle() || type.equals(BundleType.JAVA_TOOLS)) {
                bottomAnchor = NbiPanel.ANCHOR_FULL;
            }*/

            if(backgroundImage!=null) {
                leftImagePanel.setBackgroundImage(backgroundImage, NbiPanel.ANCHOR_FULL);               
            }
            if(topLeftImage!=null) {
                leftImagePanel.setBackgroundImage(topLeftImage,NbiPanel.ANCHOR_TOP_LEFT);
                width   = leftImagePanel.getBackgroundImage(NbiPanel.ANCHOR_TOP_LEFT).getIconWidth();
                height += leftImagePanel.getBackgroundImage(NbiPanel.ANCHOR_TOP_LEFT).getIconHeight();
            }
            if(bottomLeftImage!=null) {
                leftImagePanel.setBackgroundImage(bottomLeftImage, NbiPanel.ANCHOR_BOTTOM_LEFT);
                width   = leftImagePanel.getBackgroundImage(NbiPanel.ANCHOR_BOTTOM_LEFT).getIconWidth();
                height += leftImagePanel.getBackgroundImage(NbiPanel.ANCHOR_BOTTOM_LEFT).getIconHeight();
            }
            if(backgroundImage != null) {
                width  = leftImagePanel.getBackgroundImage(NbiPanel.ANCHOR_FULL).getIconWidth();
                height = leftImagePanel.getBackgroundImage(NbiPanel.ANCHOR_FULL).getIconHeight();
            }
             
            leftImagePanel.setPreferredSize(new Dimension(width,height));
            leftImagePanel.setMaximumSize(new Dimension(width,height));
            leftImagePanel.setMinimumSize(new Dimension(width,0));
            leftImagePanel.setSize(new Dimension(width,height));
            
            leftImagePanel.setOpaque(false);
            // this /////////////////////////////////////////////////////////////////
            int dy = 0;
            add(leftImagePanel, new GridBagConstraints(
                    0, 0,                             // x, y
                    1, 100,                           // width, height
                    0.0, 1.0,                         // weight-x, weight-y
                    GridBagConstraints.WEST,     // anchor
                    GridBagConstraints.VERTICAL,          // fill
                    new Insets(0, 0, 0, 0),           // padding
                    0, 0));                           // padx, pady - ???
            add(textPane, new GridBagConstraints(
                    1, dy++,                             // x, y
                    4, 1,                             // width, height
                    1.0, 0.0,                         // weight-x, weight-y
                    GridBagConstraints.LINE_START,        // anchor
                    GridBagConstraints.HORIZONTAL,          // fill
                    new Insets(10, 11, 11, 11),        // padding
                    0, 0));                           // padx, pady - ???
            detailsWarningIconLabel = new NbiLabel();
            add(detailsWarningIconLabel, new GridBagConstraints(
                    1, dy,                             // x, y
                    1, 1,                             // width, height
                    0.0, 0.0,                         // weight-x, weight-y
                    GridBagConstraints.NORTHWEST,        // anchor
                    GridBagConstraints.NONE,          // fill
                    new Insets(2, 11, 0, 0),        // padding
                    0, 0));                           // padx, pady - ???
            add(detailsTextPane, new GridBagConstraints(
                    2, dy++,                             // x, y
                    3, 1,                             // width, height
                    1.0, 0.0,                         // weight-x, weight-y
                    GridBagConstraints.WEST,        // anchor
                    GridBagConstraints.HORIZONTAL,          // fill
                    new Insets(2, 11, 0, 11),        // padding
                    0, 0));                           // padx, pady - ???
            NbiTextPane separatorPane =  new NbiTextPane();
            BundleType type = BundleType.getType(
                    System.getProperty(WELCOME_PAGE_TYPE_PROPERTY));
            if(!type.equals(BundleType.JAVAEE) && !type.equals(BundleType.RUBY) &&
                    !type.equals(BundleType.JAVA_TOOLS) && !type.equals(BundleType.MYSQL)) {
                add(scrollPane, new GridBagConstraints(
                        1, dy++,                           // x, y
                        4, 1,                              // width, height
                        1.0, 10.0,                         // weight-x, weight-y
                        GridBagConstraints.LINE_START,     // anchor
                        GridBagConstraints.BOTH,           // fill
                        new Insets(0, 11, 0, 11),            // padding
                        0, 0));                            // padx, pady - ???
            }else {
                for (RegistryNode node: registryNodes) {
                    if (node instanceof Product) {
                        final Product product = (Product) node;
                        if(product.getUid().equals("glassfish") ||
                                product.getUid().equals("glassfish-mod") ||
                                product.getUid().equals("glassfish-mod-sun") ||
                                product.getUid().equals("tomcat") ||                             
				product.getUid().equals("mysql")) {
                            final NbiCheckBox chBox;
                            if (product.getStatus() == Status.INSTALLED) {
                                chBox = new NbiCheckBox();
                                chBox.setText( "<html>" +
                                        StringUtils.format(
                                        panel.getProperty(WELCOME_TEXT_PRODUCT_INSTALLED_TEMPLATE_PROPERTY),
                                        node.getDisplayName()));
                                chBox.setSelected(true);
                                chBox.setEnabled(false);
                            } else if (product.getStatus() == Status.INSTALLED_DIFFERENT_BUILD) {
                                chBox = new NbiCheckBox();
                                chBox.setText("<html>" +
                                        StringUtils.format(
                                        panel.getProperty(WELCOME_TEXT_PRODUCT_DIFFERENT_BUILD_INSTALLED_TEMPLATE_PROPERTY),
                                        node.getDisplayName()));
                                chBox.setSelected(false);
                                chBox.setEnabled(false);
                            } else if (product.getStatus() == Status.TO_BE_INSTALLED) {
                                chBox = new NbiCheckBox();
                                chBox.setText("<html>" +
                                        StringUtils.format(
                                        panel.getProperty(WELCOME_TEXT_PRODUCT_NOT_INSTALLED_TEMPLATE_PROPERTY),
                                        node.getDisplayName()));
                                chBox.setSelected(true);
                                chBox.setEnabled(true);
                            } else if (product.getStatus() == Status.NOT_INSTALLED) {
                                chBox = new NbiCheckBox();
                                chBox.setText("<html>" +
                                        StringUtils.format(
                                        panel.getProperty(WELCOME_TEXT_PRODUCT_NOT_INSTALLED_TEMPLATE_PROPERTY),
                                        node.getDisplayName()));
                                chBox.setSelected(false);
                                chBox.setEnabled(true);
                            } else {
                                chBox = null;
                            }
                            if(chBox != null) {
                                chBox.setOpaque(false);
                                
                                //chBox.setPreferredSize(new Dimension(chBox.getPreferredSize().width,
                                //        chBox.getPreferredSize().height-2));
                                chBox.setBorder(new EmptyBorder(0,0,0,0));
                                add(chBox,new GridBagConstraints(
                                        1, dy++,                             // x, y
                                        4, 1,                             // width, height
                                        1.0, 0.0,                         // weight-x, weight-y
                                        GridBagConstraints.LINE_START,        // anchor
                                        GridBagConstraints.HORIZONTAL,          // fill
                                        new Insets(0, 11, 0, 0),        // padding
                                        0, 0));
                                chBox.addActionListener(new ActionListener() {
                                    public void actionPerformed(ActionEvent e) {
                                        if(chBox.isSelected()) {
                                            product.setStatus(Status.TO_BE_INSTALLED);
                                        } else {
                                            product.setStatus(Status.NOT_INSTALLED);
                                        }
                                        updateErrorMessage();
                                        updateSizes();
                                    }
                                });
                                
                            }
                        }
                    }
                }
                add(separatorPane , new GridBagConstraints(
                        1, dy++,                             // x, y
                        4, 1,                                // width, height
                        1.0, 2.0,                            // weight-x, weight-y
                        GridBagConstraints.LINE_START,       // anchor
                        GridBagConstraints.BOTH,             // fill
                        new Insets(0, 0, 0, 0),              // padding
                        0, 0));                              // padx, pady - ???
            }
            add(customizeButton, new GridBagConstraints(
                    1, dy,                            // x, y
                    2, 1,                             // width, height
                    1.0, 0.0,                         // weight-x, weight-y
                    GridBagConstraints.LINE_START,    // anchor
                    GridBagConstraints.NONE,          // fill
                    new Insets(10, 11, 0, 0),         // padding
                    0, 0));                           // padx, pady - ???
            separatorPane =  new NbiTextPane();
            add(separatorPane , new GridBagConstraints(
                    3, dy,                            // x, y
                    1, 1,                             // width, height
                    1.0, 0.0,                         // weight-x, weight-y
                    GridBagConstraints.CENTER,        // anchor
                    GridBagConstraints.BOTH,          // fill
                    new Insets(0, 0, 0, 0),           // padding
                    0, 0));                           // padx, pady - ???
            
            add(installationSizeLabel, new GridBagConstraints(
                    4, dy,                            // x, y
                    1, 1,                             // width, height
                    0.0, 0.0,                         // weight-x, weight-y
                    GridBagConstraints.EAST,          // anchor
                    GridBagConstraints.HORIZONTAL,    // fill
                    new Insets(10, 11, 0, 11),         // padding
                    0, 0));                           // padx, pady - ???
            
            // move error label after the left welcome image
            Component errorLabel = getComponent(0);
            getLayout().removeLayoutComponent(errorLabel);
            add(errorLabel, new GridBagConstraints(
                    1, 99,                             // x, y
                    99, 1,                             // width, height
                    1.0, 0.0,                          // weight-x, weight-y
                    GridBagConstraints.CENTER,         // anchor
                    GridBagConstraints.HORIZONTAL,     // fill
                    new Insets(4, 11, 4, 0),          // padding
                    0, 0));                            // ??? (padx, pady)
            
            // platform-specific tweak //////////////////////////////////////////////
            if (SystemUtils.isMacOS()) {
                customizeButton.setOpaque(false);
            }
            
            if(type.equals(BundleType.CUSTOMIZE) || type.equals(BundleType.JAVA) ||
                    type.equals(BundleType.JAVA_TOOLS)) {
                customizeButton.setVisible(true);
            } else {
                customizeButton.setVisible(false);
            }  
        }