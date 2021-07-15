  public void run() {
    logger.info("Task Run()");
    Thread.currentThread().setName("Informa Update Channel Task");
    /**
     * ChannelBuilder is not re-entrant and it is shared by all the
     * UpdateChannelTasks which are created by single ChannelRegistry.
     * Note that all the beginTransaction() must have a corresponding endTransaction()
     */
    synchronized (builder) {
      if (!info.getFormatDetected())
        /**
         * If this is the first time we see this Channel, then we will now attempt
         * to parse it and if this works we remember the format and proceed.
         * Otherwise we trigger error case handling and eventually deactivate it.
         */
        {
        try {
          builder.beginTransaction();
          ChannelFormat format =
            FormatDetector.getFormat(channel.getLocation());
          channel.setFormat(format);
          info.setFormatDetected(true);
          channel.setLastUpdated(new Date());
          builder.endTransaction();
        } catch (UnsupportedFormatException ex) {
          logger.info("Unsupported format for Channel");
          incrementProblems(ex);
          return;
        } catch (IOException ioe) {
          logger.info("Cannot retrieve Channel");
          incrementProblems(ioe);
          return;
        } catch (ChannelBuilderException e) {
          e.printStackTrace();
        }
      }
      try {
        synchronized (channel) {
          builder.beginTransaction();
          ChannelIF tempChannel =
            FeedParser.parse(tempBuilder, channel.getLocation());
          logger.info(
            "Updating channel from "
              + channel.getLocation()
              + ": "
              + tempChannel
              + "(new)    "
              + channel
              + "(old)");
          InformaUtils.copyChannelProperties(tempChannel, channel);
          builder.update(channel);
          channel.setLastUpdated(new Date());
          // compare with existing items, only add new ones
          if (tempChannel.getItems().isEmpty()) {
            logger.warn("No items found in channel " + channel);
          } else {
            Iterator it = tempChannel.getItems().iterator();
            while (it.hasNext()) {
              ItemIF item = (ItemIF) it.next();
              if (!channel.getItems().contains(item)) {
                logger.debug("Found new item: " + item);
                channel.addItem(builder.createItem(null, item));
                //                                                              }
              }
            } // while more items
          }
          builder.endTransaction();
        }
      } catch (ParseException pe) {
        incrementProblems(pe);
      } catch (IOException ioe) {
        incrementProblems(ioe);
      } catch (ChannelBuilderException e) {
        e.printStackTrace();
      }
    }
  }