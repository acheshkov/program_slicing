void run()
   {
      // Set the re-invite
      if (user_profile.re_invite_time>0)
      {  ua.reInvite(user_profile.contact_url,user_profile.re_invite_time);
      }

      // Set the transfer (REFER)
      if (user_profile.transfer_to!=null && user_profile.transfer_time>0)
      {  ua.callTransfer(user_profile.transfer_to,user_profile.transfer_time);
      }

      if (user_profile.do_unregister_all)
      // ########## unregisters ALL contact URLs
      {  ua.printLog("UNREGISTER ALL contact URLs");
         unregisterall();
      } 

      if (user_profile.do_unregister)
      // unregisters the contact URL
      {  ua.printLog("UNREGISTER the contact URL");
         unregister();
      } 

      if (user_profile.do_register)
      // ########## registers the contact URL with the registrar server
      {  ua.printLog("REGISTRATION");
         loopRegister(user_profile.expires,user_profile.expires/2,user_profile.keepalive_time);
      } 

      if (user_profile.call_to!=null)
      // ########## make a call with the remote URL
      {  ua.printLog("UAC: CALLING "+user_profile.call_to);
         jComboBox1.setSelectedItem(null);
         comboBoxEditor1.setItem(user_profile.call_to);
         ua.call(user_profile.call_to);       
      } 

      if (!user_profile.audio && !user_profile.video) ua.printLog("ONLY SIGNALING, NO MEDIA");   
   }