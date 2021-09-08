@Override
        protected void initialize() {
            final Registry registry = Registry.getInstance();
            
            final boolean errorsEncountered =
                    registry.getProducts(FAILED_TO_INSTALL).size() > 0 &&
                    registry.getProducts(FAILED_TO_UNINSTALL).size() > 0;
            final boolean warningsEncountered =
                    registry.getProducts(INSTALLED_WITH_WARNINGS).size() > 0 &&
                    registry.getProducts(UNINSTALLED_WITH_WARNINGS).size() > 0;
            
            if (errorsEncountered) {
                messagePane.setContentType(component.getProperty(MESSAGE_ERRORS_CONTENT_TYPE_PROPERTY));
                messagePane.setText(component.getProperty(MESSAGE_ERRORS_TEXT_PROPERTY));
            } else if (warningsEncountered) {
                messagePane.setContentType(component.getProperty(MESSAGE_WARNINGS_CONTENT_TYPE_PROPERTY));
                messagePane.setText(component.getProperty(MESSAGE_WARNINGS_TEXT_PROPERTY));
            } else {
                messagePane.setContentType(component.getProperty(MESSAGE_SUCCESS_CONTENT_TYPE_PROPERTY));
                messagePane.setText(component.getProperty(MESSAGE_SUCCESS_TEXT_PROPERTY));
            }
            
            List<Product> products;
            
            products = registry.getProducts(INSTALLED_SUCCESSFULLY);
            if (products.size() > 0) {
                successfullyInstalledComponentsLabel.setVisible(true);
                successfullyInstalledComponentsPane.setVisible(true);
                
                successfullyInstalledComponentsLabel.setText(component.getProperty(SUCCESSFULLY_INSTALLED_LABEL_TEXT_PROPERTY));
                successfullyInstalledComponentsPane.setContentType(component.getProperty(SUCCESSFULLY_INSTALLED_CONTENT_TYPE_PROPERTY));
                successfullyInstalledComponentsPane.setText(StringUtils.format(component.getProperty(SUCCESSFULLY_INSTALLED_TEXT_PROPERTY), StringUtils.asString(products, component.getProperty(COMPONENTS_LIST_SEPARATOR_PROPERTY))));
            } else {
                successfullyInstalledComponentsLabel.setVisible(false);
                successfullyInstalledComponentsPane.setVisible(false);
            }
            
            products = registry.getProducts(INSTALLED_WITH_WARNINGS);
            if (products.size() > 0) {
                componentsInstalledWithWarningsLabel.setVisible(true);
                componentsInstalledWithWarningsPane.setVisible(true);
                
                componentsInstalledWithWarningsLabel.setText(component.getProperty(INSTALLED_WITH_WARNINGS_LABEL_TEXT_PROPERTY));
                componentsInstalledWithWarningsPane.setContentType(component.getProperty(INSTALLED_WITH_WARNINGS_CONTENT_TYPE_PROPERTY));
                componentsInstalledWithWarningsPane.setText(StringUtils.format(component.getProperty(INSTALLED_WITH_WARNINGS_TEXT_PROPERTY), StringUtils.asString(products, component.getProperty(COMPONENTS_LIST_SEPARATOR_PROPERTY))));
            } else {
                componentsInstalledWithWarningsLabel.setVisible(false);
                componentsInstalledWithWarningsPane.setVisible(false);
            }
            
            products = registry.getProducts(FAILED_TO_INSTALL);
            if (products.size() > 0) {
                componentsFailedToInstallLabel.setVisible(true);
                componentsFailedToInstallPane.setVisible(true);
                
                componentsFailedToInstallLabel.setText(component.getProperty(FAILED_TO_INSTALL_WARNINGS_LABEL_TEXT_PROPERTY));
                componentsFailedToInstallPane.setContentType(component.getProperty(FAILED_TO_INSTALL_CONTENT_TYPE_PROPERTY));
                componentsFailedToInstallPane.setText(StringUtils.format(component.getProperty(FAILED_TO_INSTALL_TEXT_PROPERTY), StringUtils.asString(products, component.getProperty(COMPONENTS_LIST_SEPARATOR_PROPERTY))));
            } else {
                componentsFailedToInstallLabel.setVisible(false);
                componentsFailedToInstallPane.setVisible(false);
            }
            
            products = registry.getProducts(UNINSTALLED_SUCCESSFULLY);
            if (products.size() > 0) {
                successfullyUninstalledComponentsLabel.setVisible(true);
                successfullyUninstalledComponentsPane.setVisible(true);
                
                successfullyUninstalledComponentsLabel.setText(component.getProperty(SUCCESSFULLY_UNINSTALLED_LABEL_TEXT_PROPERTY));
                successfullyUninstalledComponentsPane.setContentType(component.getProperty(SUCCESSFULLY_UNINSTALLED_CONTENT_TYPE_PROPERTY));
                successfullyUninstalledComponentsPane.setText(StringUtils.format(component.getProperty(SUCCESSFULLY_UNINSTALLED_TEXT_PROPERTY), StringUtils.asString(products, component.getProperty(COMPONENTS_LIST_SEPARATOR_PROPERTY))));
            } else {
                successfullyUninstalledComponentsLabel.setVisible(false);
                successfullyUninstalledComponentsPane.setVisible(false);
            }
            
            List<Product> notCompletelyRemoved = new LinkedList<Product>();
            for (Product product: products) {
                if (!FileUtils.isEmpty(product.getInstallationLocation())) {
                    notCompletelyRemoved.add(product);
                }
            }
            
            if (notCompletelyRemoved.size() > 0) {
                final String text = successfullyUninstalledComponentsPane.getText();
                successfullyUninstalledComponentsPane.setText(text + StringUtils.format(
                        component.getProperty(MESSAGE_FILES_REMAINING_PROPERTY),
                        StringUtils.asString(notCompletelyRemoved)));
            }
            
            products = registry.getProducts(UNINSTALLED_WITH_WARNINGS);
            if (products.size() > 0) {
                componentsUninstalledWithWarningsLabel.setVisible(true);
                componentsUninstalledWithWarningsPane.setVisible(true);
                
                componentsUninstalledWithWarningsLabel.setText(component.getProperty(UNINSTALLED_WITH_WARNINGS_LABEL_TEXT_PROPERTY));
                componentsUninstalledWithWarningsPane.setContentType(component.getProperty(UNINSTALLED_WITH_WARNINGS_CONTENT_TYPE_PROPERTY));
                componentsUninstalledWithWarningsPane.setText(StringUtils.format(component.getProperty(UNINSTALLED_WITH_WARNINGS_TEXT_PROPERTY), StringUtils.asString(products, component.getProperty(COMPONENTS_LIST_SEPARATOR_PROPERTY))));
            } else {
                componentsUninstalledWithWarningsLabel.setVisible(false);
                componentsUninstalledWithWarningsPane.setVisible(false);
            }
            
            notCompletelyRemoved = new LinkedList<Product>();
            for (Product product: products) {
                if (!FileUtils.isEmpty(product.getInstallationLocation())) {
                    notCompletelyRemoved.add(product);
                }
            }
            
            if (notCompletelyRemoved.size() > 0) {
                final String text = componentsUninstalledWithWarningsPane.getText();
                componentsUninstalledWithWarningsPane.setText(text + StringUtils.format(
                        component.getProperty(MESSAGE_FILES_REMAINING_PROPERTY),
                        StringUtils.asString(notCompletelyRemoved)));
            }
            
            products = registry.getProducts(FAILED_TO_UNINSTALL);
            if (products.size() > 0) {
                componentsFailedToUninstallLabel.setVisible(true);
                componentsFailedToUninstallPane.setVisible(true);
                
                componentsFailedToUninstallLabel.setText(component.getProperty(FAILED_TO_UNINSTALL_WARNINGS_LABEL_TEXT_PROPERTY));
                componentsFailedToUninstallPane.setContentType(component.getProperty(FAILED_TO_UNINSTALL_CONTENT_TYPE_PROPERTY));
                componentsFailedToUninstallPane.setText(StringUtils.format(component.getProperty(FAILED_TO_UNINSTALL_TEXT_PROPERTY), StringUtils.asString(products, component.getProperty(COMPONENTS_LIST_SEPARATOR_PROPERTY))));
            } else {
                componentsFailedToUninstallLabel.setVisible(false);
                componentsFailedToUninstallPane.setVisible(false);
            }
            
            final String viewDetailsButtonText = component.getProperty(VIEW_DETAILS_BUTTON_TEXT_PROPERTY);
            viewDetailsButton.setText(StringUtils.stripMnemonic(viewDetailsButtonText));
            viewDetailsButton.setMnemonic(StringUtils.fetchMnemonic(viewDetailsButtonText));
            
            final String viewLogButtonText = component.getProperty(VIEW_LOG_BUTTON_TEXT_PROPERTY);
            viewLogButton.setText(StringUtils.stripMnemonic(viewLogButtonText));
            viewLogButton.setMnemonic(StringUtils.fetchMnemonic(viewLogButtonText));
            
            final String sendLogButtonText = component.getProperty(SEND_LOG_BUTTON_TEXT_PROPERTY);
            sendLogButton.setText(StringUtils.stripMnemonic(sendLogButtonText));
            sendLogButton.setMnemonic(StringUtils.fetchMnemonic(sendLogButtonText));
        }