/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2017-2020. All rights reserved.
 */
package com.huawei.mergebot.model;

import com.huawei.mergebot.conflictresolving.ConflictResolvingEngine;
import com.huawei.mergebot.model.mergerule.OperationType;

import java.util.Comparator;
import java.util.List;

/**
 * The type Training sample.
 *
 * @since 4.3.3
 */
public class TrainingSample implements Comparator<TrainingSample>, Comparable<TrainingSample> {
    /**
     * The Base file path.
     */

    // raw inputs
    public String baseFilePath;
    /**
     * The Version a file path.
     */
    public String versionAFilePath;
    /**
     * The Version b file path.
     */
    public String versionBFilePath;
    /**
     * The Manual merged file path.
     */
    public String manualMergedFilePath;
    /**
     * The Git merged file path.
     */
    public String gitMergedFilePath;
    /**
     * The Starting line of conflict block.
     */
    public Integer startingLineOfConflictBlock;
    /**
     * The Entity id.
     */
    public String entityID;

    /**
     * The Base content str.
     */
    public String baseContentStr;
    /**
     * The Base content array.
     */
    public List<String> baseContentArray;
    /**
     * The Version a content str.
     */
    public String versionAContentStr;
    /**
     * The Version a content array.
     */
    public List<String> versionAContentArray;
    /**
     * The Version b content str.
     */
    public String versionBContentStr;
    /**
     * The Version b content array.
     */
    public List<String> versionBContentArray;
    /**
     * The Manual merged str.
     */
    public String manualMergedStr;
    /**
     * The Manual merged array.
     */
    public List<String> manualMergedArray;
    /**
     * The Version a operation type.
     */
    public OperationType versionAOperationType = OperationType.NONE;
    /**
     * The Version b operation type.
     */
    public OperationType versionBOperationType = OperationType.NONE;

    // input features
    // intra-revision metrics: [0: base; 1: mergeTo; 2: mergeFrom]

    /**
     * The Intra revision syntactic features.
     */
    public int[][] intraRevisionSyntacticFeatures = new int[3][11];

    // inter-revision metrics: [0: base; 1: mergeTo; 2: mergeFrom]

    /**
     * The Inter revision diff features.
     */
    public double[][] interRevisionDiffFeatures = new double[3][12];

    /**
     * The Remark.
     */
    public String remark = ConflictResolvingEngine.REMARK;

    /**
     * The Oracle merge solution.
     */

    // output features
    public MergeSolutionType oracleMergeSolution = MergeSolutionType.OTHERS;
    /**
     * The Predicted merge solution.
     */
    public MergeSolutionType predictedMergeSolution = MergeSolutionType.OTHERS;

    /**
     * Sets raw metrics.
     *
     * @param conflictEntity the conflict entity
     */
    public void setRawMetrics(ThreeWayConflictEntity conflictEntity) {
        if (conflictEntity.ownerBlock != null && conflictEntity.ownerBlock.ownerFileSet != null) {
            baseFilePath = conflictEntity.ownerBlock.ownerFileSet.getPath(ThreeWayModel.BASE);
            versionAFilePath = conflictEntity.ownerBlock.ownerFileSet.getPath(ThreeWayModel.OURS);
            versionBFilePath = conflictEntity.ownerBlock.ownerFileSet.getPath(ThreeWayModel.THEIRS);
            manualMergedFilePath = conflictEntity.ownerBlock.ownerFileSet.getPath(ThreeWayModel.MANUAL);
            gitMergedFilePath = conflictEntity.ownerBlock.ownerFileSet.getPath(ThreeWayModel.MANUAL);
            startingLineOfConflictBlock = conflictEntity.ownerBlock.startingLine;
        }

        entityID = conflictEntity.entityID;
        baseContentStr = conflictEntity.getContentStr(ThreeWayModel.BASE);
        this.baseContentArray = conflictEntity.getContent(ThreeWayModel.BASE);
        versionAContentStr = conflictEntity.getContentStr(ThreeWayModel.OURS);
        this.versionAContentArray = conflictEntity.getContent(ThreeWayModel.OURS);
        versionBContentStr = conflictEntity.getContentStr(ThreeWayModel.THEIRS);
        this.versionBContentArray = conflictEntity.getContent(ThreeWayModel.THEIRS);

        this.manualMergedArray = conflictEntity.getContent(ThreeWayModel.MANUAL);
        manualMergedStr = conflictEntity.getContentStr(ThreeWayModel.MANUAL);

        versionAOperationType = conflictEntity.getOperationType(ThreeWayModel.OURS);
        versionBOperationType = conflictEntity.getOperationType(ThreeWayModel.THEIRS);
    }

    @Override
    public int compareTo(TrainingSample o) {
        // TODO Auto-generated method stub
        return 0;
    }

    @Override
    public int compare(TrainingSample o1, TrainingSample o2) {
        // TODO Auto-generated method stub
        return 0;
    }

    /**
     * Extract intra revision syntactic features.
     *
     * @param synFeatures the syn features
     * @param i the
     */
    public void extractIntraRevisionSyntacticFeatures(SyntacticFeatureSet synFeatures, int i) {
        // intra-revision metrics: [0: base; 1: mergeTo; 2: mergeFrom]
        int[] result = intraRevisionSyntacticFeatures[i];
        result[0] = synFeatures.isOnlyContainComments() ? 1 : 0;
        result[1] = synFeatures.commentNumber;
        result[2] = synFeatures.codeStatementNumber;
        result[3] = synFeatures.newlyDefinedVariables.size();
        result[4] = synFeatures.newlyInitiatedObjects.size();
        result[5] = synFeatures.usedPreviousVariables.size();
        result[6] = synFeatures.forStmtNumber;
        result[7] = synFeatures.whileStmtNumber;
        result[8] = synFeatures.foreachStmtNumber;
        result[9] = synFeatures.ifOrElseBranchNumber;
        result[10] = synFeatures.getMethodCallees().size();
    }

    /**
     * Extract inter revision syntactic features.
     *
     * @param featureId the feature id
     * @param sourceFeatures the source features
     * @param targetFeatures the target features
     */
    public void extractInterRevisionSyntacticFeatures(
            int featureId, SyntacticFeatureSet sourceFeatures, SyntacticFeatureSet targetFeatures) {
        int sharedVariables = 0;
        int newlyAdded = 0;
        int newlyDeleted = 0;
        for (String var : targetFeatures.usedPreviousVariables) {
            if (sourceFeatures.usedPreviousVariables.contains(var)) {
                sharedVariables++;
            } else {
                newlyAdded++;
            }
        }

        if (sourceFeatures.usedPreviousVariables.size() == 0) {
            this.interRevisionDiffFeatures[featureId][0] = 0;
        } else {
            this.interRevisionDiffFeatures[featureId][0] =
                    sharedVariables * 1.0 / sourceFeatures.usedPreviousVariables.size();
        }

        this.interRevisionDiffFeatures[featureId][1] = newlyAdded;
        this.interRevisionDiffFeatures[featureId][2] = newlyDeleted;

        // o mergeTo����ֵ���������У���base�����ͬ������������������������������
        sharedVariables = 0;
        newlyAdded = 0;
        newlyDeleted = 0;
        for (String var : targetFeatures.assignedVariables) {
            if (sourceFeatures.assignedVariables.contains(var)) {
                sharedVariables++;
            } else {
                newlyAdded++;
            }
        }

        if (sourceFeatures.assignedVariables.size() == 0) {
            this.interRevisionDiffFeatures[featureId][3] = 0;
        } else {
            this.interRevisionDiffFeatures[featureId][3] =
                    sharedVariables * 1.0 / sourceFeatures.assignedVariables.size();
        }

        this.interRevisionDiffFeatures[featureId][4] = newlyAdded;
        this.interRevisionDiffFeatures[featureId][5] = newlyDeleted;

        // o mergeTo��new�Ķ��󼯺��У���base�����ͬ������������������������������
        sharedVariables = 0;
        newlyAdded = 0;
        newlyDeleted = 0;
        for (String var : targetFeatures.newlyInitiatedObjects) {
            if (sourceFeatures.newlyInitiatedObjects.contains(var)) {
                sharedVariables++;
            } else {
                newlyAdded++;
            }
        }

        if (sourceFeatures.newlyInitiatedObjects.size() == 0) {
            this.interRevisionDiffFeatures[featureId][6] =
                    sharedVariables * 1.0 / sourceFeatures.newlyInitiatedObjects.size();
        } else {
            this.interRevisionDiffFeatures[featureId][6] =
                    sharedVariables * 1.0 / sourceFeatures.newlyInitiatedObjects.size();
        }

        this.interRevisionDiffFeatures[featureId][7] = newlyAdded;
        this.interRevisionDiffFeatures[featureId][8] = newlyDeleted;

        // o mergeTo�����õķ��������У���base�����ͬ������������������������������
        // o mergeTo�����õ���伯���У���base�����ͬ������������������������������
        sharedVariables = 0;
        newlyAdded = 0;
        newlyDeleted = 0;
        for (String var : targetFeatures.methodCallees) {
            if (sourceFeatures.methodCallees.contains(var)) {
                sharedVariables++;
            } else {
                newlyAdded++;
            }
        }

        if (sourceFeatures.methodCallees.size() == 0) {
            this.interRevisionDiffFeatures[featureId][9] = 0;
        } else {
            this.interRevisionDiffFeatures[featureId][9] = sharedVariables * 1.0 / sourceFeatures.methodCallees.size();
        }

        this.interRevisionDiffFeatures[featureId][10] = newlyAdded;
        this.interRevisionDiffFeatures[featureId][11] = newlyDeleted;
    }
}
