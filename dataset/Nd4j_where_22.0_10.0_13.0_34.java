public static INDArray[] where(INDArray condition, INDArray x, INDArray y){
        Preconditions.checkState((x == null && y == null) || (x != null && y != null), "Both X and Y must be" +
                "null, or neither must be null");
        DynamicCustomOp.DynamicCustomOpsBuilder op = DynamicCustomOp.builder("where_np");
        List<LongShapeDescriptor> outShapes;
        if(x == null){
            //First case: condition only...
            op.addInputs(condition);
        } else {
            if(!x.equalShapes(y) || !x.equalShapes(condition)){
                //noinspection ConstantConditions
                Preconditions.throwStateEx("Shapes must be equal: condition=%s, x=%s, y=%s", condition.shape(), x.shape(), y.shape());
            }
            op.addInputs(condition, x, y);
        }
        DynamicCustomOp o = op.build();
        outShapes = Nd4j.getExecutioner().calculateOutputShape(o);
        INDArray[] outputs = new INDArray[outShapes.size()];

        if(x == null && (outShapes.get(0) == null || outShapes.get(0).getShape().length == 0 || outShapes.get(0).getShape()[0] == 0)){
            //Empty: no conditions match
            for( int i=0; i<outputs.length; i++ ){
                outputs[i]  = Nd4j.empty();
            }
            return outputs;
        }

        for(int i=0; i<outputs.length; i++){
            outputs[i] = Nd4j.create(outShapes.get(i), false);
        }
        op.addOutputs(outputs);

        Nd4j.getExecutioner().execAndReturn(op.build());
        return outputs;
    }