public void run(String command, String arguments[], Context context, PrintStream out) throws DDRInteractiveCommandException 
	{
		if (arguments.length != 3) {
			out.println("Unexpected number of arguments.");
			printUsage(out);
			return;
		}
		
		long address = 0L;
		if (arguments[0].startsWith("0x")) {
			address = Long.parseLong(arguments[0].substring(2 /* 0x */), 16);
		} else {
			address = Long.parseLong(arguments[0], 16);
		}
		
		int length = 0;
		if (arguments[1].startsWith("0x")) {
			length = Integer.parseInt(arguments[1].substring(2 /* 0x */), 16);
		} else {
			length = Integer.parseInt(arguments[1], 16);
		}
		
		String filename = arguments[2];
		FileOutputStream fos;
		try {
			fos = new FileOutputStream(filename);
		} catch (FileNotFoundException e) {
			throw new DDRInteractiveCommandException("Failed to open output file " + filename, e);
		}
		
		try {
			byte[] data = new byte[length];
			context.process.getBytesAt(address, data);
			try {
				fos.write(data, 0, length);
			} catch (IOException e) {
				throw new DDRInteractiveCommandException("Failed to write data to file " + filename, e);
			} finally {
				try {
					fos.close();
				} catch (IOException e) {
					/* Whatcha gonna do? */
				}
			}
		} catch (MemoryFault e) {
			throw new DDRInteractiveCommandException("Unable to read memory range", e);
		}
	}