@Override
        public String getColumnText(Object element, int columnIndex)
        {
            DBDAttributeBinding binding = (DBDAttributeBinding) element;
            DBDAttributeConstraint constraint = getBindingConstraint(binding);
            switch (columnIndex) {
                case 0: return constraint.getAttribute().getName();
                case 1: return String.valueOf(constraint.getOriginalVisualPosition() + 1);
                case 2: {
                    int orderPosition = constraint.getOrderPosition();
                    if (orderPosition > 0) {
                        return " " + String.valueOf(orderPosition);
                    }
                    return ""; //$NON-NLS-1$
                }
                case 3: {
                    DBCExecutionContext executionContext = resultSetViewer.getExecutionContext();
                    if (executionContext != null) {
                        String condition = SQLUtils.getConstraintCondition(executionContext.getDataSource(), constraint, true);
                        if (condition != null) {
                            return condition;
                        }
                    }
                    return ""; //$NON-NLS-1$
                }
                default: return ""; //$NON-NLS-1$
            }
        }