/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2017-2020. All rights reserved.
 */
package com.huawei.mergebot.dao.ui;

import com.huawei.mergebot.dao.RestClient;
import com.huawei.mergebot.model.ui.CommitIds;
import com.huawei.mergebot.model.ui.Repo;
import com.huawei.mergebot.model.ui.ResolveParameters;
import com.huawei.mergebot.utils.PropertiesUtil;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;

/**
 * The type Reo dao.
 *
 * @since 4.3.3
 */
public class ReoDAO {
    /**
     * Update commit i ds.
     *
     * @param repoID the repo id
     * @param oursCommitID the ours commit id
     * @param theirCommitID the their commit id
     */
    public static void updateCommitIDs(String repoID, String oursCommitID, String theirCommitID) {
        CommitIds commitIDs = new CommitIds().oursCommitId(oursCommitID).theirsCommitId(theirCommitID);
        String conflictFileEndPoint = PropertiesUtil.getValue("MergebotServer") + "/repos/" + repoID + "/commit_ids";
        RestTemplate restTemplate = new RestTemplate();
        restTemplate.put(conflictFileEndPoint, commitIDs);
    }

    /**
     * Register repo.
     *
     * @param repo the repo
     */
    public static void registerRepo(Repo repo) {
        RestTemplate restTemplate = new RestTemplate();
        String conflictFileEndPoint = PropertiesUtil.getValue("MergebotServer") + "/repos/register?force=true";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Repo> entity = new HttpEntity<Repo>(repo, headers);
        ResponseEntity<Repo> resp = restTemplate.exchange(conflictFileEndPoint, HttpMethod.PUT, entity, Repo.class);
    }

    /**
     * Get repo.
     *
     * @param repoID the repo id
     * @return the repo
     */
    public static Repo get(String repoID) {
        String projectURL = PropertiesUtil.getValue("MergebotServer") + "/repos/" + repoID;
        RestClient client = new RestClient();
        Repo returnResults = client.getForObjectOperate(projectURL, new HashMap<String, Object>(), Repo.class);
        return returnResults;
    }

    /**
     * Update resolved parameters.
     *
     * @param repoID the repo id
     * @param resolveParameters the resolve parameters
     */
    public static void updateResolvedParameters(String repoID, ResolveParameters resolveParameters) {
        String conflictFileEndPoint =
                PropertiesUtil.getValue("MergebotServer") + "/repos/" + repoID + "/resolve_parameters";
        RestTemplate restTemplate = new RestTemplate();
        restTemplate.put(conflictFileEndPoint, resolveParameters);
    }

    /**
     * Resolve archive repo.
     *
     * @param repoID the repo id
     */
    public static void resolveArchiveRepo(String repoID) {
        String conflictFileEndPoint =
                PropertiesUtil.getValue("MergebotServer") + "/repos/" + repoID + "/resolve_archive_repo";
        RestTemplate restTemplate = new RestTemplate();
        restTemplate.put(conflictFileEndPoint, null);
    }
}
