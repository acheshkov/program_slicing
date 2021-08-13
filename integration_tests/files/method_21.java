    public String getClientId(FacesContext context)
    {
        if (context == null)
            throw new NullPointerException("context");

        if (_clientId != null)
            return _clientId;

        String id = getId();
        if (id == null)
        {
            UniqueIdVendor parentUniqueIdVendor = _ComponentUtils.findParentUniqueIdVendor(this);
            if (parentUniqueIdVendor == null)
            {
                UIViewRoot viewRoot = context.getViewRoot();
                if (viewRoot != null)
                {
                    id = viewRoot.createUniqueId();
                }
                else
                {
                    // The RI throws a NPE
                    String location = getComponentLocation(this);
                    throw new FacesException("Cannot create clientId. No id is assigned for component"
                            + " to create an id and UIViewRoot is not defined: "
                            + getPathToComponent(this)
                            + (location != null ? " created from: " + location : ""));
                }
            }
            else
            {
                id = parentUniqueIdVendor.createUniqueId(context, null);
            }
            setId(id);
        }

        UIComponent namingContainer = _ComponentUtils.findParentNamingContainer(this, false);
        if (namingContainer != null)
        {
            String containerClientId = namingContainer.getContainerClientId(context);
            if (containerClientId != null)
            {
                StringBuilder bld = __getSharedStringBuilder();
                _clientId = bld.append(containerClientId).append(UINamingContainer.getSeparatorChar(context)).append(id).toString();
            }
            else
            {
                _clientId = id;
            }
        }
        else
        {
            _clientId = id;
        }

        Renderer renderer = getRenderer(context);
        if (renderer != null)
        {
            _clientId = renderer.convertClientId(context, _clientId);
        }

        return _clientId;
    }
    