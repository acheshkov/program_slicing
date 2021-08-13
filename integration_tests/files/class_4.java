/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2017-2020. All rights reserved.
 */
package com.huawei.mergebot.archive;

import com.huawei.mergebot.codeanalysis.xml.XMLFileWhiteListUtil;
import com.huawei.mergebot.conflictresolving.AutoResolvedGenerator;
import com.huawei.mergebot.conflictresolving.resolver.FileSetResolver;
import com.huawei.mergebot.dao.ArchivesDAO;
import com.huawei.mergebot.dao.ui.ConflictFileDAO;
import com.huawei.mergebot.dao.ui.ReoDAO;
import com.huawei.mergebot.model.ConflictHandleMode;
import com.huawei.mergebot.model.MergeResultRenderingMode;
import com.huawei.mergebot.model.ThreeWayConflictFileSet;
import com.huawei.mergebot.model.ui.ConflictFile;
import com.huawei.mergebot.model.ui.ConflictFile.StatusEnum;
import com.huawei.mergebot.model.ui.Repo;
import com.huawei.mergebot.model.ui.ResolveParameters;
import com.huawei.mergebot.model.helps.ConflictFileHelper;
import com.huawei.mergebot.utils.FileUtil;

import java.io.IOException;
import java.util.List;
import java.util.UUID;

/**
 * The type Repo resolver.
 *
 * @since 4.3.3
 */
public class RepoResolver {
    /**
     * Resolver string.
     *
     * @param originalRepoId the original repo id
     * @return the string
     * @throws IOException the io exception
     */
    public String resolver(String originalRepoId) throws IOException {
        Repo repo = ReoDAO.get(originalRepoId);
        if (repo == null) {
            return null;
        }
        ResolveParameters resolveParameters = repo.getResolveParameters();
        FileSetResolver resolver =
                new FileSetResolver(
                        resolveParameters.isEnableAutoResolve(),
                        MergeResultRenderingMode.getEnum(resolveParameters.getMergeRenderingMode().toString()),
                        resolveParameters.isEnableAIMode(),
                        resolveParameters.isIsPython3(),
                        resolveParameters.isEnableAuthorAnalysis(),
                        resolveParameters.isEnableRename(),
                        resolveParameters.isEnableComplicateRule());

        List<String> relativePaths = ArchivesDAO.getFilePathList(originalRepoId, "gitMerged/");

        String repoId = originalRepoId;

        XMLFileWhiteListUtil xmlFileWhiteListUtil =
                new XMLFileWhiteListUtil(resolveParameters.getWhiteListPathContent());

        String taskId = UUID.randomUUID().toString();
        for (String relativePath : relativePaths) {
            relativePath = relativePath.substring("gitMerged/".length());
            ThreeWayFilePath threeWayFilePath =
                    new ThreeWayFilePath(
                            System.getProperty("java.io.tmpdir") + "/mergebot/" + taskId + "/" + repoId, relativePath);
            FileUtil.writeFileInOverideMode(
                    threeWayFilePath.getFullFilePath("base"),
                    ArchivesDAO.getOriginalConflictFile(originalRepoId, threeWayFilePath.getVersionFilePath("base")),
                    "UTF-8");
            FileUtil.writeFileInOverideMode(
                    threeWayFilePath.getFullFilePath("ours"),
                    ArchivesDAO.getOriginalConflictFile(originalRepoId, threeWayFilePath.getVersionFilePath("ours")),
                    "UTF-8");
            FileUtil.writeFileInOverideMode(
                    threeWayFilePath.getFullFilePath("theirs"),
                    ArchivesDAO.getOriginalConflictFile(originalRepoId, threeWayFilePath.getVersionFilePath("theirs")),
                    "UTF-8");
            FileUtil.writeFileInOverideMode(
                    threeWayFilePath.getFullFilePath("gitMerged"),
                    ArchivesDAO.getOriginalConflictFile(
                            originalRepoId, threeWayFilePath.getVersionFilePath("gitMerged")),
                    "UTF-8");
            String manualContent =
                    ArchivesDAO.getOriginalConflictFile(
                            originalRepoId, threeWayFilePath.getVersionFilePath("manualMerged"));
            if (manualContent.isEmpty()) {
                continue;
            }
            FileUtil.writeFileInOverideMode(threeWayFilePath.getFullFilePath("manualMerged"), manualContent, "UTF-8");
            ConflictHandleMode conflictHandleModeEnum = ConflictHandleMode.KEEP_CONFLICT;
            if (xmlFileWhiteListUtil.whetherInWhiteList(relativePath)) {
                conflictHandleModeEnum =
                        ConflictHandleMode.getEnum(resolveParameters.getConflictHandleMode().toString());
            }
            ThreeWayConflictFileSet fileSet =
                    resolver.autoResolveConflicts(
                            "",
                            threeWayFilePath.getFullFilePath("base"),
                            threeWayFilePath.getFullFilePath("ours"),
                            threeWayFilePath.getFullFilePath("theirs"),
                            threeWayFilePath.getFullFilePath("gitMerged"),
                            threeWayFilePath.getFullFilePath("manualMerged"),
                            conflictHandleModeEnum);

            if (fileSet == null) {
                continue;
            }

            AutoResolvedGenerator.generateAutoResolvedFileOptimized(
                    fileSet,
                    threeWayFilePath.getFullFilePath("mergebotMerged"),
                    threeWayFilePath.getFullFilePath("mergebotMerged_backUp"));
            ArchivesDAO.postOriginalConflictFIle(
                    threeWayFilePath.getFullFilePath("mergebotMerged"),
                    threeWayFilePath.getVersionFilePath("mergebotMerged"),
                    originalRepoId);

            putArchiveConflictFile(originalRepoId, repoId, relativePath, fileSet);
        }
        return repoId;
    }

    private void putArchiveConflictFile(String originalRepoId, String repoId, String relativePath,
            ThreeWayConflictFileSet fileSet) {
        ConflictFile conflictFile = ConflictFileHelper.extractForOnlineReview(fileSet, "base/" + relativePath);
        conflictFile.setRepoId(repoId);
        conflictFile.setForkFromRepoId(originalRepoId);
        conflictFile.setStatus(StatusEnum.CONFLICTING);
        ConflictFileDAO.putArchiveConflictFile(conflictFile);
    }
}
