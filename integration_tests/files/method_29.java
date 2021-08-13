    public  Point2D[] intersectionPoint() { 

        Point2D[] result = null;
        if (itsc==null) return null;
        else if ( itsc.length == 2 ) {
            if ( !isNaN(itsc[0]) ) {
                result = new Point2D[1];
                result[0] = AlgoLine2D.evaluate(line0,itsc[0]); 
            } else if ( !isNaN(itsc[1]) ) {
                result = new Point2D[1];
                result[0] = AlgoLine2D.evaluate(line0,itsc[1]); 
            } else {
                result = null;
            }
        } else if ( itsc.length == 4 ) {
            int count = 0;
            int index[] = new int[4];
            if (!isNaN(itsc[0])) index[count++] = 0;
            if (!isNaN(itsc[1])) index[count++] = 1;
            if (!isNaN(itsc[2])) index[count++] = 2;
            if (!isNaN(itsc[3])) index[count++] = 3;
            Line2D l0 = (index[0]<2) ? line0 : line1;
            Line2D l1 = (index[1]<2) ? line0 : line1;
            result = new Point2D[2];
            if (count==0) {
                result = null;
            } else if (count==2) {
                if ((itsc[index[0]]==0.0 || itsc[index[0]]==1.0) && 
                    (itsc[index[1]]==0.0 || itsc[index[1]]==1.0)) {
                    /** colinear touching the boundaries */
                    result = new Point2D[1];
                    result[0] = AlgoLine2D.evaluate(l0,itsc[index[0]]); 
                } else {
                    /** colinear overlaping interiors */
                    result = new Point2D[2];
                    result[0] = AlgoLine2D.evaluate(l0,itsc[index[0]]); 
                    result[1] = AlgoLine2D.evaluate(l1,itsc[index[1]]); 
                }
            } else if (count==3) {
                if (index[0]<2 && index[1]<2) {
                    result[0] = AlgoLine2D.evaluate(l0,itsc[index[0]]); 
                    result[1] = AlgoLine2D.evaluate(l0,itsc[index[1]]); 
                } else {
                    result[0] = AlgoLine2D.evaluate(l1,itsc[index[0]]); 
                    result[1] = AlgoLine2D.evaluate(l1,itsc[index[1]]);                     
                }

            } else if (count==4) {
                result[0] = AlgoLine2D.evaluate(l0,itsc[index[0]]); 
                result[1] = AlgoLine2D.evaluate(l0,itsc[index[1]]);                 
            }

        }
        return result;
    }