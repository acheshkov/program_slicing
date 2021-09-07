@Override
    public void deployMessageDestinations(Set<MessageDestination> destinations) throws ConfigurationException {
        Set<MessageDestination> deployedDestinations = getMessageDestinations();
        // for faster searching
        Map<String, MessageDestination> deployed = createMap(deployedDestinations);

        // will contain all ds which do not conflict with existing ones
        List<WildflyMessageDestination> toDeploy = new ArrayList<WildflyMessageDestination>();

        // resolve all conflicts
        LinkedList<MessageDestination> conflictJMS = new LinkedList<MessageDestination>();
        for (MessageDestination destination : destinations) {
            if (!(destination instanceof WildflyMessageDestination)) {
                LOGGER.log(Level.INFO, "Unable to deploy {0}", destination);
                continue;
            }

            WildflyMessageDestination jbossMessageDestination = (WildflyMessageDestination) destination;
            String name = jbossMessageDestination.getName();
            Set<String> jndiNames = new HashSet<String>(jbossMessageDestination.getJndiNames());
            jndiNames.retainAll(deployed.keySet());
            if (deployed.keySet().contains(jbossMessageDestination.getName()) || !jndiNames.isEmpty()) { // conflicting destination found
                MessageDestination deployedMessageDestination = deployed.get(name);
                // name is same, but message dest differs
                if (!deployedMessageDestination.equals(jbossMessageDestination)) {
                    conflictJMS.add(deployed.get(name));
                }
            }else {
                toDeploy.add(jbossMessageDestination);
            }
        }

        if (!conflictJMS.isEmpty()) {
            // TODO exception or nothing ?
        }
        ProgressObject po = dm.deployMessageDestinations(toDeploy);

        ProgressObjectSupport.waitFor(po);

        if (po.getDeploymentStatus().isFailed()) {
            String msg = NbBundle.getMessage(WildflyMessageDestinationManager.class, "MSG_FailedToDeployJMS");
            throw new ConfigurationException(msg);
        }
    }