private void processEventForNewTimelineService(HistoryEvent event,
      JobId jobId, long timestamp) {
    org.apache.hadoop.yarn.api.records.timelineservice.TimelineEntity tEntity =
        null;
    String taskId = null;
    String taskAttemptId = null;
    boolean setCreatedTime = false;
    long taskIdPrefix = 0;
    long taskAttemptIdPrefix = 0;

    switch (event.getEventType()) {
    // Handle job events
    case JOB_SUBMITTED:
      setCreatedTime = true;
      break;
    case JOB_STATUS_CHANGED:
    case JOB_INFO_CHANGED:
    case JOB_INITED:
    case JOB_PRIORITY_CHANGED:
    case JOB_QUEUE_CHANGED:
    case JOB_FAILED:
    case JOB_KILLED:
    case JOB_ERROR:
    case JOB_FINISHED:
    case AM_STARTED:
    case NORMALIZED_RESOURCE:
      break;
    // Handle task events
    case TASK_STARTED:
      setCreatedTime = true;
      taskId = ((TaskStartedEvent)event).getTaskId().toString();
      taskIdPrefix = TimelineServiceHelper.
          invertLong(((TaskStartedEvent)event).getStartTime());
      break;
    case TASK_FAILED:
      taskId = ((TaskFailedEvent)event).getTaskId().toString();
      taskIdPrefix = TimelineServiceHelper.
          invertLong(((TaskFailedEvent)event).getStartTime());
      break;
    case TASK_UPDATED:
      taskId = ((TaskUpdatedEvent)event).getTaskId().toString();
      break;
    case TASK_FINISHED:
      taskId = ((TaskFinishedEvent)event).getTaskId().toString();
      taskIdPrefix = TimelineServiceHelper.
          invertLong(((TaskFinishedEvent)event).getStartTime());
      break;
    case MAP_ATTEMPT_STARTED:
    case REDUCE_ATTEMPT_STARTED:
      setCreatedTime = true;
      taskId = ((TaskAttemptStartedEvent)event).getTaskId().toString();
      taskAttemptId = ((TaskAttemptStartedEvent)event).
          getTaskAttemptId().toString();
      taskAttemptIdPrefix = TimelineServiceHelper.
          invertLong(((TaskAttemptStartedEvent)event).getStartTime());
      break;
    case CLEANUP_ATTEMPT_STARTED:
    case SETUP_ATTEMPT_STARTED:
      taskId = ((TaskAttemptStartedEvent)event).getTaskId().toString();
      taskAttemptId = ((TaskAttemptStartedEvent)event).
          getTaskAttemptId().toString();
      break;
    case MAP_ATTEMPT_FAILED:
    case CLEANUP_ATTEMPT_FAILED:
    case REDUCE_ATTEMPT_FAILED:
    case SETUP_ATTEMPT_FAILED:
    case MAP_ATTEMPT_KILLED:
    case CLEANUP_ATTEMPT_KILLED:
    case REDUCE_ATTEMPT_KILLED:
    case SETUP_ATTEMPT_KILLED:
      taskId = ((TaskAttemptUnsuccessfulCompletionEvent)event).
          getTaskId().toString();
      taskAttemptId = ((TaskAttemptUnsuccessfulCompletionEvent)event).
          getTaskAttemptId().toString();
      taskAttemptIdPrefix = TimelineServiceHelper.invertLong(
          ((TaskAttemptUnsuccessfulCompletionEvent)event).getStartTime());
      break;
    case MAP_ATTEMPT_FINISHED:
      taskId = ((MapAttemptFinishedEvent)event).getTaskId().toString();
      taskAttemptId = ((MapAttemptFinishedEvent)event).
          getAttemptId().toString();
      taskAttemptIdPrefix = TimelineServiceHelper.
          invertLong(((MapAttemptFinishedEvent)event).getStartTime());
      break;
    case REDUCE_ATTEMPT_FINISHED:
      taskId = ((ReduceAttemptFinishedEvent)event).getTaskId().toString();
      taskAttemptId = ((ReduceAttemptFinishedEvent)event).
          getAttemptId().toString();
      taskAttemptIdPrefix = TimelineServiceHelper.
          invertLong(((ReduceAttemptFinishedEvent)event).getStartTime());
      break;
    case SETUP_ATTEMPT_FINISHED:
    case CLEANUP_ATTEMPT_FINISHED:
      taskId = ((TaskAttemptFinishedEvent)event).getTaskId().toString();
      taskAttemptId = ((TaskAttemptFinishedEvent)event).
          getAttemptId().toString();
      break;
    default:
      LOG.warn("EventType: " + event.getEventType() + " cannot be recognized" +
          " and handled by timeline service.");
      return;
    }

    org.apache.hadoop.yarn.api.records.timelineservice.TimelineEntity
        appEntityWithJobMetrics = null;
    if (taskId == null) {
      // JobEntity
      tEntity = createJobEntity(event, timestamp, jobId,
          MAPREDUCE_JOB_ENTITY_TYPE, setCreatedTime);
      if (event.getEventType() == EventType.JOB_FINISHED
          && event.getTimelineMetrics() != null) {
        appEntityWithJobMetrics = createAppEntityWithJobMetrics(event, jobId);
      }
    } else {
      if (taskAttemptId == null) {
        // TaskEntity
        tEntity = createTaskEntity(event, timestamp, taskId,
            MAPREDUCE_TASK_ENTITY_TYPE, MAPREDUCE_JOB_ENTITY_TYPE,
            jobId, setCreatedTime, taskIdPrefix);
      } else {
        // TaskAttemptEntity
        tEntity = createTaskAttemptEntity(event, timestamp, taskAttemptId,
            MAPREDUCE_TASK_ATTEMPT_ENTITY_TYPE, MAPREDUCE_TASK_ENTITY_TYPE,
            taskId, setCreatedTime, taskAttemptIdPrefix);
      }
    }
    try {
      if (appEntityWithJobMetrics == null) {
        timelineV2Client.putEntitiesAsync(tEntity);
      } else {
        timelineV2Client.putEntities(tEntity, appEntityWithJobMetrics);
      }
    } catch (IOException | YarnException e) {
      LOG.error("Failed to process Event " + event.getEventType()
          + " for the job : " + jobId, e);
      return;
    }
    if (event.getEventType() == EventType.JOB_SUBMITTED) {
      // Publish configs after main job submitted event has been posted.
      publishConfigsOnJobSubmittedEvent((JobSubmittedEvent)event, jobId);
    }
  }