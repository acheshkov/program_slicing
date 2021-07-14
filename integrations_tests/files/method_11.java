    public void validate(Object object, String context, ValidatorContext validatorContext, String method) throws ValidationException {
        List<Validator> validators = getValidators(object.getClass(), context, method);
        Set<String> shortcircuitedFields = null;

        for (final Validator validator : validators) {
        try {
                validator.setValidatorContext(validatorContext);

                if (LOG.isDebugEnabled()) {
                    LOG.debug("Running validator: " + validator + " for object " + object + " and method " + method);
                }

                FieldValidator fValidator = null;
                String fullFieldName = null;

                if (validator instanceof FieldValidator) {
                    fValidator = (FieldValidator) validator;
                    fullFieldName = new InternalValidatorContextWrapper(fValidator.getValidatorContext()).getFullFieldName(fValidator.getFieldName());

                    // This is pretty crap, but needed to support short-circuited validations on nested visited objects
                    if (validatorContext instanceof VisitorFieldValidator.AppendingValidatorContext) {
                        VisitorFieldValidator.AppendingValidatorContext appendingValidatorContext =
                                (VisitorFieldValidator.AppendingValidatorContext) validatorContext;
                        fullFieldName = appendingValidatorContext.getFullFieldNameFromParent(fValidator.getFieldName());
                    }

                    if ((shortcircuitedFields != null) && shortcircuitedFields.contains(fullFieldName)) {
                        if (LOG.isDebugEnabled()) {
                            LOG.debug("Short-circuited, skipping");
                        }

                        continue;
                    }
                }

                if (validator instanceof ShortCircuitableValidator && ((ShortCircuitableValidator) validator).isShortCircuit()) {
                    // get number of existing errors
                    List<String> errs = null;

                    if (fValidator != null) {
                        if (validatorContext.hasFieldErrors()) {
                            Collection<String> fieldErrors = validatorContext.getFieldErrors().get(fullFieldName);

                            if (fieldErrors != null) {
                                errs = new ArrayList<String>(fieldErrors);
                            }
                        }
                    } else if (validatorContext.hasActionErrors()) {
                        Collection<String> actionErrors = validatorContext.getActionErrors();

                        if (actionErrors != null) {
                            errs = new ArrayList<String>(actionErrors);
                        }
                    }

                    validator.validate(object);

                    if (fValidator != null) {
                        if (validatorContext.hasFieldErrors()) {
                            Collection<String> errCol = validatorContext.getFieldErrors().get(fullFieldName);

                            if ((errCol != null) && !errCol.equals(errs)) {
                                if (LOG.isDebugEnabled()) {
                                    LOG.debug("Short-circuiting on field validation");
                                }

                                if (shortcircuitedFields == null) {
                                    shortcircuitedFields = new TreeSet<String>();
                                }

                                shortcircuitedFields.add(fullFieldName);
                            }
                        }
                    } else if (validatorContext.hasActionErrors()) {
                        Collection<String> errCol = validatorContext.getActionErrors();

                        if ((errCol != null) && !errCol.equals(errs)) {
                            if (LOG.isDebugEnabled()) {
                                LOG.debug("Short-circuiting");
                            }

                            break;
                        }
                    }

                    continue;
                }

                validator.validate(object);
            }
            finally {
                validator.setValidatorContext(null);
            }
        }
    }