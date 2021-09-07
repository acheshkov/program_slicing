@Override
    public Optional<PlanNodeStatsEstimate> doCalculate(RowNumberNode node, StatsProvider statsProvider, Lookup lookup, Session session, TypeProvider types)
    {
        PlanNodeStatsEstimate sourceStats = statsProvider.getStats(node.getSource());
        if (sourceStats.isOutputRowCountUnknown()) {
            return Optional.empty();
        }
        double sourceRowsCount = sourceStats.getOutputRowCount();

        double partitionCount = 1;
        for (VariableReferenceExpression groupByVariable : node.getPartitionBy()) {
            VariableStatsEstimate variableStatistics = sourceStats.getVariableStatistics(groupByVariable);
            int nullRow = (variableStatistics.getNullsFraction() == 0.0) ? 0 : 1;
            // assuming no correlation between grouping keys
            partitionCount *= variableStatistics.getDistinctValuesCount() + nullRow;
        }
        partitionCount = min(sourceRowsCount, partitionCount);

        if (isNaN(partitionCount)) {
            return Optional.empty();
        }

        // assuming no skew
        double rowsPerPartition = sourceRowsCount / partitionCount;
        if (node.getMaxRowCountPerPartition().isPresent()) {
            rowsPerPartition = min(rowsPerPartition, node.getMaxRowCountPerPartition().get());
        }

        double outputRowsCount = sourceRowsCount;
        if (node.getMaxRowCountPerPartition().isPresent()) {
            outputRowsCount = partitionCount * rowsPerPartition;
        }

        return Optional.of(PlanNodeStatsEstimate.buildFrom(sourceStats)
                .setOutputRowCount(outputRowsCount)
                .addVariableStatistics(node.getRowNumberVariable(), VariableStatsEstimate.builder()
                        // Note: if we assume no skew, we could also estimate highValue
                        // (as rowsPerPartition), but underestimation of highValue may have
                        // more severe consequences than underestimation of distinctValuesCount
                        .setLowValue(1)
                        .setDistinctValuesCount(rowsPerPartition)
                        .setNullsFraction(0.0)
                        .setAverageRowSize(BIGINT.getFixedSize())
                        .build())
                .build());
    }