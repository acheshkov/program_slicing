@POST
    @Timed
    @ApiOperation(value = "Add a widget to a dashboard")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    @ApiResponses(value = {
            @ApiResponse(code = 404, message = "Dashboard not found."),
            @ApiResponse(code = 400, message = "Validation error."),
            @ApiResponse(code = 400, message = "No such widget type."),
    })
    @AuditEvent(type = AuditEventTypes.DASHBOARD_WIDGET_CREATE)
    public Response addWidget(
            @ApiParam(name = "dashboardId", required = true)
            @PathParam("dashboardId") String dashboardId,
            @ApiParam(name = "JSON body", required = true) AddWidgetRequest awr) throws ValidationException, NotFoundException {
        checkPermission(RestPermissions.DASHBOARDS_EDIT, dashboardId);

        // Bind to streams for reader users and check stream permission.
        if (awr.config().containsKey("stream_id")) {
            checkPermission(RestPermissions.STREAMS_READ, (String) awr.config().get("stream_id"));
        } else {
            checkPermission(RestPermissions.SEARCHES_ABSOLUTE);
            checkPermission(RestPermissions.SEARCHES_RELATIVE);
            checkPermission(RestPermissions.SEARCHES_KEYWORD);
        }

        final DashboardWidget widget;
        try {
            widget = dashboardWidgetCreator.fromRequest(awr, getCurrentUser().getName());

            final Dashboard dashboard = dashboardService.load(dashboardId);

            dashboardService.addWidget(dashboard, widget);
        } catch (DashboardWidget.NoSuchWidgetTypeException e2) {
            LOG.debug("No such widget type.", e2);
            throw new BadRequestException("No such widget type.", e2);
        } catch (InvalidRangeParametersException e3) {
            LOG.debug("Invalid timerange parameters provided.", e3);
            throw new BadRequestException("Invalid timerange parameters provided.", e3);
        } catch (InvalidWidgetConfigurationException e4) {
            LOG.debug("Invalid widget configuration.", e4);
            throw new BadRequestException("Invalid widget configuration.", e4);
        }

        final Map<String, String> result = ImmutableMap.of("widget_id", widget.getId());
        final URI widgetUri = getUriBuilderToSelf().path(DashboardWidgetsResource.class, "getWidget")
                .build(dashboardId, widget.getId());

        return Response.created(widgetUri).entity(result).build();
    }