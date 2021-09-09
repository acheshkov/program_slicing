public JSONObject doSrvIPXT(String namespaceId, String serviceName, String agent, String clusters, String clientIP,
                                int udpPort,
                                String env, boolean isCheck, String app, String tid, boolean healthyOnly)
        throws Exception {

        ClientInfo clientInfo = new ClientInfo(agent);
        JSONObject result = new JSONObject();
        Service service = serviceManager.getService(namespaceId, serviceName);

        if (service == null) {
            if (Loggers.SRV_LOG.isDebugEnabled()) {
                Loggers.SRV_LOG.debug("no instance to serve for service: {}", serviceName);
            }
            result.put("name", serviceName);
            result.put("clusters", clusters);
            result.put("hosts", new JSONArray());
            return result;
        }

        checkIfDisabled(service);

        long cacheMillis = switchDomain.getDefaultCacheMillis();

        // now try to enable the push
        try {
            if (udpPort > 0 && pushService.canEnablePush(agent)) {

                pushService.addClient(namespaceId, serviceName,
                    clusters,
                    agent,
                    new InetSocketAddress(clientIP, udpPort),
                    pushDataSource,
                    tid,
                    app);
                cacheMillis = switchDomain.getPushCacheMillis(serviceName);
            }
        } catch (Exception e) {
            Loggers.SRV_LOG.error("[NACOS-API] failed to added push client {}, {}:{}", clientInfo, clientIP, udpPort, e);
            cacheMillis = switchDomain.getDefaultCacheMillis();
        }

        List<Instance> srvedIPs;

        srvedIPs = service.srvIPs(Arrays.asList(StringUtils.split(clusters, ",")));

        // filter ips using selector:
        if (service.getSelector() != null && StringUtils.isNotBlank(clientIP)) {
            srvedIPs = service.getSelector().select(clientIP, srvedIPs);
        }

        if (CollectionUtils.isEmpty(srvedIPs)) {

            if (Loggers.SRV_LOG.isDebugEnabled()) {
                Loggers.SRV_LOG.debug("no instance to serve for service: {}", serviceName);
            }

            if (clientInfo.type == ClientInfo.ClientType.JAVA &&
                clientInfo.version.compareTo(VersionUtil.parseVersion("1.0.0")) >= 0) {
                result.put("dom", serviceName);
            } else {
                result.put("dom", NamingUtils.getServiceName(serviceName));
            }

            result.put("hosts", new JSONArray());
            result.put("name", serviceName);
            result.put("cacheMillis", cacheMillis);
            result.put("lastRefTime", System.currentTimeMillis());
            result.put("checksum", service.getChecksum());
            result.put("useSpecifiedURL", false);
            result.put("clusters", clusters);
            result.put("env", env);
            result.put("metadata", service.getMetadata());
            return result;
        }

        Map<Boolean, List<Instance>> ipMap = new HashMap<>(2);
        ipMap.put(Boolean.TRUE, new ArrayList<>());
        ipMap.put(Boolean.FALSE, new ArrayList<>());

        for (Instance ip : srvedIPs) {
            ipMap.get(ip.isHealthy()).add(ip);
        }

        if (isCheck) {
            result.put("reachProtectThreshold", false);
        }

        double threshold = service.getProtectThreshold();

        if ((float) ipMap.get(Boolean.TRUE).size() / srvedIPs.size() <= threshold) {

            Loggers.SRV_LOG.warn("protect threshold reached, return all ips, service: {}", serviceName);
            if (isCheck) {
                result.put("reachProtectThreshold", true);
            }

            ipMap.get(Boolean.TRUE).addAll(ipMap.get(Boolean.FALSE));
            ipMap.get(Boolean.FALSE).clear();
        }

        if (isCheck) {
            result.put("protectThreshold", service.getProtectThreshold());
            result.put("reachLocalSiteCallThreshold", false);

            return new JSONObject();
        }

        JSONArray hosts = new JSONArray();

        for (Map.Entry<Boolean, List<Instance>> entry : ipMap.entrySet()) {
            List<Instance> ips = entry.getValue();

            if (healthyOnly && !entry.getKey()) {
                continue;
            }

            for (Instance instance : ips) {

                // remove disabled instance:
                if (!instance.isEnabled()) {
                    continue;
                }

                JSONObject ipObj = new JSONObject();

                ipObj.put("ip", instance.getIp());
                ipObj.put("port", instance.getPort());
                // deprecated since nacos 1.0.0:
                ipObj.put("valid", entry.getKey());
                ipObj.put("healthy", entry.getKey());
                ipObj.put("marked", instance.isMarked());
                ipObj.put("instanceId", instance.getInstanceId());
                ipObj.put("metadata", instance.getMetadata());
                ipObj.put("enabled", instance.isEnabled());
                ipObj.put("weight", instance.getWeight());
                ipObj.put("clusterName", instance.getClusterName());
                if (clientInfo.type == ClientInfo.ClientType.JAVA &&
                    clientInfo.version.compareTo(VersionUtil.parseVersion("1.0.0")) >= 0) {
                    ipObj.put("serviceName", instance.getServiceName());
                } else {
                    ipObj.put("serviceName", NamingUtils.getServiceName(instance.getServiceName()));
                }

                ipObj.put("ephemeral", instance.isEphemeral());
                hosts.add(ipObj);

            }
        }

        result.put("hosts", hosts);
        if (clientInfo.type == ClientInfo.ClientType.JAVA &&
            clientInfo.version.compareTo(VersionUtil.parseVersion("1.0.0")) >= 0) {
            result.put("dom", serviceName);
        } else {
            result.put("dom", NamingUtils.getServiceName(serviceName));
        }
        result.put("name", serviceName);
        result.put("cacheMillis", cacheMillis);
        result.put("lastRefTime", System.currentTimeMillis());
        result.put("checksum", service.getChecksum());
        result.put("useSpecifiedURL", false);
        result.put("clusters", clusters);
        result.put("env", env);
        result.put("metadata", service.getMetadata());
        return result;
    }