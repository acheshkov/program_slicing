public void addToMenu(Toolbar toolbar, int position) {
        MenuItem menuItem = toolbar.getMenu().add(Menu.NONE, position, position, button.text.get(""));
        if (button.showAsAction.hasValue()) menuItem.setShowAsAction(button.showAsAction.get());
        menuItem.setEnabled(button.enabled.isTrueOrUndefined());
        menuItem.setOnMenuItemClickListener(this);
        if (button.hasComponent()) {
            menuItem.setActionView(getView());
            if (button.accessibilityLabel.hasValue()) getView().setContentDescription(button.accessibilityLabel.get());
        } else {
            if (button.accessibilityLabel.hasValue()) MenuItemCompat.setContentDescription(menuItem, button.accessibilityLabel.get());
            if (button.hasIcon()) {
                loadIcon(new ImageLoadingListenerAdapter() {
                    @Override
                    public void onComplete(@NonNull Drawable icon) {
                        TitleBarButtonController.this.icon = icon;
                        setIconColor(icon);
                        menuItem.setIcon(icon);
                    }
                });
            } else {
                optionsPresenter.setTextColor();
                if (button.fontSize.hasValue()) optionsPresenter.setFontSize(menuItem);
                optionsPresenter.setTypeFace(button.fontFamily);
            }
        }
        setTestId(toolbar, button.testId);
    }