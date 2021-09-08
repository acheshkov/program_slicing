private Pair<INDArray, INDArray> convertWritablesSequence(List<List<List<Writable>>> list, int minValues,
                    int maxTSLength, SubsetDetails details, int[] longestSequence, long rngSeed) {
        if (maxTSLength == -1)
            maxTSLength = list.get(0).size();
        INDArray arr;

        if (list.get(0).isEmpty()) {
            throw new ZeroLengthSequenceException("Zero length sequence encountered");
        }

        List<Writable> firstStep = list.get(0).get(0);

        int size = 0;
        if (details.entireReader) {
            //Need to account for NDArrayWritables etc in list:
            for (Writable w : firstStep) {
                if (w instanceof NDArrayWritable) {
                    size += ((NDArrayWritable) w).get().size(1);
                } else {
                    size++;
                }
            }
        } else if (details.oneHot) {
            size = details.oneHotNumClasses;
        } else {
            //Need to account for NDArrayWritables etc in list:
            for (int i = details.subsetStart; i <= details.subsetEndInclusive; i++) {
                Writable w = firstStep.get(i);
                if (w instanceof NDArrayWritable) {
                    size += ((NDArrayWritable) w).get().size(1);
                } else {
                    size++;
                }
            }
        }
        arr = Nd4j.create(new int[] {minValues, size, maxTSLength}, 'f');

        boolean needMaskArray = false;
        for (List<List<Writable>> c : list) {
            if (c.size() < maxTSLength)
                needMaskArray = true;
        }

        if (needMaskArray && alignmentMode == AlignmentMode.EQUAL_LENGTH) {
            throw new UnsupportedOperationException(
                            "Alignment mode is set to EQUAL_LENGTH but variable length data was "
                                            + "encountered. Use AlignmentMode.ALIGN_START or AlignmentMode.ALIGN_END with variable length data");
        }

        INDArray maskArray;
        if (needMaskArray) {
            maskArray = Nd4j.ones(minValues, maxTSLength);
        } else {
            maskArray = null;
        }

        //Don't use the global RNG as we need repeatability for each subset (i.e., features and labels must be aligned)
        Random rng = null;
        if (timeSeriesRandomOffset) {
            rng = new Random(rngSeed);
        }

        for (int i = 0; i < minValues; i++) {
            List<List<Writable>> sequence = list.get(i);

            //Offset for alignment:
            int startOffset;
            if (alignmentMode == AlignmentMode.ALIGN_START || alignmentMode == AlignmentMode.EQUAL_LENGTH) {
                startOffset = 0;
            } else {
                //Align end
                //Only practical differences here are: (a) offset, and (b) masking
                startOffset = longestSequence[i] - sequence.size();
            }

            if (timeSeriesRandomOffset) {
                int maxPossible = maxTSLength - sequence.size() + 1;
                startOffset = rng.nextInt(maxPossible);
            }

            int t = 0;
            int k;
            for (List<Writable> timeStep : sequence) {
                k = startOffset + t++;

                if (details.entireReader) {
                    //Convert entire reader contents, without modification
                    Iterator<Writable> iter = timeStep.iterator();
                    int j = 0;
                    while (iter.hasNext()) {
                        Writable w = iter.next();

                        if (w instanceof NDArrayWritable) {
                            INDArray row = ((NDArrayWritable) w).get();

                            arr.put(new INDArrayIndex[] {NDArrayIndex.point(i),
                                            NDArrayIndex.interval(j, j + row.length()), NDArrayIndex.point(k)}, row);
                            j += row.length();
                        } else {
                            arr.putScalar(i, j, k, w.toDouble());
                            j++;
                        }
                    }
                } else if (details.oneHot) {
                    //Convert a single column to a one-hot representation
                    Writable w = null;
                    if (timeStep instanceof List)
                        w = timeStep.get(details.subsetStart);
                    else {
                        Iterator<Writable> iter = timeStep.iterator();
                        for (int x = 0; x <= details.subsetStart; x++)
                            w = iter.next();
                    }
                    int classIdx = w.toInt();
                    if (classIdx >= details.oneHotNumClasses) {
                        throw new IllegalStateException("Cannot convert sequence writables to one-hot: class index " + classIdx
                                        + " >= numClass (" + details.oneHotNumClasses + "). (Note that classes are zero-" +
                                "indexed, thus only values 0 to nClasses-1 are valid)");
                    }
                    arr.putScalar(i, classIdx, k, 1.0);
                } else {
                    //Convert a subset of the columns...
                    int l = 0;
                    for (int j = details.subsetStart; j <= details.subsetEndInclusive; j++) {
                        Writable w = timeStep.get(j);

                        if (w instanceof NDArrayWritable) {
                            INDArray row = ((NDArrayWritable) w).get();
                            arr.put(new INDArrayIndex[] {NDArrayIndex.point(i),
                                            NDArrayIndex.interval(l, l + row.length()), NDArrayIndex.point(k)}, row);

                            l += row.length();
                        } else {
                            arr.putScalar(i, l++, k, w.toDouble());
                        }
                    }
                }
            }

            //For any remaining time steps: set mask array to 0 (just padding)
            if (needMaskArray) {
                //Masking array entries at start (for align end)
                if (timeSeriesRandomOffset || alignmentMode == AlignmentMode.ALIGN_END) {
                    for (int t2 = 0; t2 < startOffset; t2++) {
                        maskArray.putScalar(i, t2, 0.0);
                    }
                }

                //Masking array entries at end (for align start)
                int lastStep = startOffset + sequence.size();
                if (timeSeriesRandomOffset || alignmentMode == AlignmentMode.ALIGN_START || lastStep < maxTSLength) {
                    for (int t2 = lastStep; t2 < maxTSLength; t2++) {
                        maskArray.putScalar(i, t2, 0.0);
                    }
                }
            }
        }

        return new Pair<>(arr, maskArray);
    }