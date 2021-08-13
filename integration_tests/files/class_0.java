/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2017-2020. All rights reserved.
 */
package com.huawei.mergebot.codeinsight;

import java.io.File;
import java.io.IOException;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

import org.apache.log4j.Logger;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.lib.Repository;
import org.springframework.web.client.RestTemplate;

import com.huawei.mergebot.model.IOpensourceProject;
import com.huawei.mergebot.model.IProjectRepo;
import com.huawei.mergebot.utils.PropertiesUtil;

/**
 * Data collection agent operate logic
 *
 * @since 4.3.3
 */
public class DCABasedOperator implements Operator {
    private static final Logger logger = Logger.getLogger(DCABasedOperator.class);
    private String projectName = "";
    private String projectPath = "";
    private String projectVersion = "";

    @Override
    public void initParm(String[] args) {
        if (args != null) {
            this.projectName = args[1];
            this.projectPath = args[2];
            this.projectVersion = args[3];
        } else if (PropertiesUtil.getValue("ERROR").equals("true")) {
            logger.error("args is null");
        }
    }

    @Override
    public void operate() {
        InsightTools gTools = new InsightTools();
        Set<String> gitPaths = new HashSet<>();
        RestTemplate restTemplate = new RestTemplate();
        InsightRestClient irestOperate = new InsightRestClient();
        String projectURL = PropertiesUtil.getValue("MergebotServer") + "opensource_project";
        String repoURL = PropertiesUtil.getValue("MergebotServer") + "project_repo";
        String commitURL = PropertiesUtil.getValue("MergebotServer") + "git_commit";

        // Processing time
        long gitstartTime = System.currentTimeMillis();
        gitPaths = gTools.getGitRepoPathsSet(new File(this.projectPath), gitPaths);

        String projectID = getProjectId(gitPaths, restTemplate, irestOperate, projectURL);

        Iterator itGitPaths = gitPaths.iterator();
        while (itGitPaths.hasNext()) {
            long starTime = System.currentTimeMillis();
            String gPath = itGitPaths.next().toString();
            // Post project all repos info to Server
            String repoID = getRepoId(restTemplate, irestOperate, repoURL, projectID, gPath);

            // Analyzing Repo and post all commits info to Server
            try {
                Repository gitRepo = gTools.openJGitRepository(gPath);
                ObjectId objectId = gTools.getHeadObjectID(gitRepo);
                gTools.analyzeCommit(gitRepo, objectId, restTemplate, commitURL, repoID, gPath);
                long gitTime = System.currentTimeMillis() - gitstartTime;
                if (PropertiesUtil.getValue("INFO").equals("true")) {
                    if (logger.isInfoEnabled()) {
                        logger.info(
                                Thread.currentThread().getName()
                                        + " Processing Consuming "
                                        + (gitTime / 1000) / 3600.00
                                        + "(Hour)");
                    }
                }

            } catch (GitAPIException ge) {
                printGitApiError(gitstartTime, gPath, ge);
            } catch (IOException e) {
                if (logger.isInfoEnabled()) {
                    logger.info("RepoName: " + gPath + " Operate JGit Error - " + e.getMessage());
                }
                long gitTime = System.currentTimeMillis() - gitstartTime;
                if (PropertiesUtil.getValue("ERROR").equals("true")) {
                    logger.error(
                            Thread.currentThread().getName()
                                    + " Processing Consuming "
                                    + (gitTime / 1000) / 3600.00
                                    + "(Hour)");
                }
            }
        }
    }

    private void printGitApiError(long gitstartTime, String gPath, GitAPIException ge) {
        if (logger.isInfoEnabled()) {
            logger.info("RepoName: " + gPath + " Operate JGit Error - " + ge.getMessage());
        }
        ge.printStackTrace();
        long gitTime = System.currentTimeMillis() - gitstartTime;
        if (PropertiesUtil.getValue("ERROR").equals("true")) {
            logger.error(
                    Thread.currentThread().getName()
                            + " Processing Consuming "
                            + (gitTime / (double)1000) / (double)3600
                            + "(Hour)");
        }
    }

    private String getRepoId(RestTemplate restTemplate, InsightRestClient irestOperate, String repoURL,
            String projectID, String gPath) {
        IProjectRepo projectRepo = new IProjectRepo();
        projectRepo.repoPath(gPath).projectId(projectID);
        String repoID = "";
        projectRepo = irestOperate.postIProjectRepo(projectRepo, restTemplate, repoURL);
        if (projectRepo == null) {
            repoID = "222222";
            if (PropertiesUtil.getValue("ERROR").equals("true")) {
                logger.error("RepoPath: " + gPath + " Post Error");
            }
        } else {
            repoID = projectRepo.getId();
            if (PropertiesUtil.getValue("INFO").equals("true")) {
                if (logger.isInfoEnabled()) {
                    logger.info("RepoPath: " + projectRepo.getRepoPath() + " Post Success");
                }
            }
        }
        return repoID;
    }

    private String getProjectId(Set<String> gitPaths, RestTemplate restTemplate, InsightRestClient irestOperate,
            String projectURL) {
        int repoNum = 0;
        if (PropertiesUtil.getValue("INFO").equals("true")) {
            for (String l : gitPaths) {
                repoNum++;
                logger.info(l);
            }
            if (logger.isInfoEnabled()) {
                logger.info("gitRepoNum: " + repoNum);
            }
        }

        // Post opensource project info to Server
        IOpensourceProject opensourceProject = new IOpensourceProject();
        opensourceProject
                .projectName(this.projectName)
                .projectPath(this.projectPath)
                .projectVersion(this.projectVersion);
        String projectID = "";
        opensourceProject = irestOperate.postIOpensourceProject(opensourceProject, restTemplate, projectURL);
        if (opensourceProject == null) {
            projectID = "111111";
            if (PropertiesUtil.getValue("ERROR").equals("true")) {
                logger.error("projectName: " + projectName + " Post Error");
            }
        } else {
            projectID = opensourceProject.getId();
            if (PropertiesUtil.getValue("INFO").equals("true")) {
                if (logger.isInfoEnabled()) {
                    logger.info("projectName: " + projectName + " Post Success");
                }
            }
        }
        return projectID;
    }
}
