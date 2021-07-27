	public static void onSystemShutdown() {
		for(Map.Entry<String, Sequence> entry:s_sequences.entrySet()) {
		//}
		//for(String key: s_sequences.keySet()) {
			String[] tokens = entry.getKey().split("\\.");
			String TableName = tokens[1];
			int AD_Client_ID = Integer.parseInt(tokens[0]);
			String selectSQL = "SELECT CurrentNext, CurrentNextSys, IncrementNo, AD_Sequence_ID "
				+ "FROM AD_Sequence "
				+ "WHERE Name=?"
				+ " AND IsActive='Y' AND IsTableID='Y' AND IsAutoSequence='Y' "
				+ " FOR UPDATE";
			Sequence seq = entry.getValue();
			//at this point there should not be a need for syncrhonization, just for safety
			synchronized(seq) {
				Trx trx = Trx.get("MSequence.onSystemShutdown()");
				PreparedStatement pstmt = null;
				ResultSet rs = null;
				try {
					//
					pstmt = trx.getConnection().prepareStatement(selectSQL, ResultSet.TYPE_FORWARD_ONLY,
							ResultSet.CONCUR_UPDATABLE);
					pstmt.setString(1, TableName);
					//
					rs = pstmt.executeQuery();
					if (rs.next()) {
						if (isCompiereSys(AD_Client_ID)) {
							int dbNextSeq = rs.getInt(2);
							// only when db nextseq equals to the jvm endseq then i'll write back. this is so if there are multiple
							//jvms running, i know that other jvms already advanced the sequenes so that i don't mess with it
							if(dbNextSeq == seq.endSeq) {
								seq.endSeq = seq.nextSeq;
								rs.updateInt(2, seq.nextSeq);
							}
						} else {
							int dbNextSeq = rs.getInt(1);
							// only when db nextseq equals to the jvm endseq then i'll write back. this is so if there are multiple
							//jvms running, i know that other jvms already advanced the sequenes so that i don't mess with it
							if(dbNextSeq == seq.endSeq) {
								seq.endSeq = seq.nextSeq;
								rs.updateInt(1, seq.nextSeq);
							}
						}
						rs.updateRow();
					}
				}catch (Exception e) {
					s_log.log(Level.SEVERE, TableName + " - " + e.getMessage(), e);
				} finally {
					if( rs != null )
						try {
							rs.close();
						} catch (SQLException e) {
							s_log.log(Level.SEVERE, "Finish", e);
						}

						if (pstmt != null)
							try {
								pstmt.close();
							} catch (SQLException e) {
								s_log.log(Level.SEVERE, "Finish", e);
							}
							pstmt = null;

							if (trx != null) {
								trx.commit();
								trx.close();
							}
				}
			}
		}
	}