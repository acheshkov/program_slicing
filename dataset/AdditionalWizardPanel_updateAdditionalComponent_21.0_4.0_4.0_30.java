private void updateAdditionalComponent(DataObject selected) {
        
        I18nSupport support = null;
        
        if (selected != null) {
            support = (sourceMap.get(selected)).getSupport();
        }
        additionalComponent.setVisible(false);
        // remove last one
        remove(additionalComponent);
        
        if(support != null && support.hasAdditionalCustomizer()) {
            additionalComponent = support.getAdditionalCustomizer();
            additionalComponent.setVisible(true);
            viewedSources.add(selected);
        } else {
            additionalComponent = EMPTY_COMPONENT;
        }

        // add it
        GridBagConstraints gridBagConstraints = new GridBagConstraints();
        gridBagConstraints.gridx = 0;
        gridBagConstraints.gridy = 1;
        gridBagConstraints.gridwidth = 2;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weightx = 1.0;
        gridBagConstraints.weighty = 1.0;
        add(additionalComponent, gridBagConstraints);
        
        revalidate();        
    }