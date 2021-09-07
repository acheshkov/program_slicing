public void updatePreemptableExtras(ResourceCalculator rc) {
    // Reset untouchableExtra and preemptableExtra
    untouchableExtra = Resources.none();
    preemptableExtra = Resources.none();

    Resource extra = Resources.subtract(getUsed(), getGuaranteed());
    if (Resources.lessThan(rc, totalPartitionResource, extra,
        Resources.none())) {
      extra = Resources.none();
    }

    if (null == children || children.isEmpty()) {
      // If it is a leaf queue
      if (preemptionDisabled) {
        untouchableExtra = extra;
      } else {
        preemptableExtra = extra;
      }
    } else {
      // If it is a parent queue
      Resource childrensPreemptable = Resource.newInstance(0, 0);
      for (TempQueuePerPartition child : children) {
        Resources.addTo(childrensPreemptable, child.preemptableExtra);
      }
      // untouchableExtra = max(extra - childrenPreemptable, 0)
      if (Resources.greaterThanOrEqual(rc, totalPartitionResource,
          childrensPreemptable, extra)) {
        untouchableExtra = Resource.newInstance(0, 0);
      } else {
        untouchableExtra = Resources.subtract(extra, childrensPreemptable);
      }
      preemptableExtra = Resources.min(rc, totalPartitionResource,
          childrensPreemptable, extra);
    }
  }