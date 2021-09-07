@PostMapping(value = "/yun", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
	public Dict yun(@RequestParam("file") MultipartFile file) {
		if (file.isEmpty()) {
			return Dict.create().set("code", 400).set("message", "文件内容为空");
		}
		String fileName = file.getOriginalFilename();
		String rawFileName = StrUtil.subBefore(fileName, ".", true);
		String fileType = StrUtil.subAfter(fileName, ".", true);
		String localFilePath = StrUtil.appendIfMissing(fileTempPath, "/") + rawFileName + "-" + DateUtil.current(false) + "." + fileType;
		try {
			file.transferTo(new File(localFilePath));
			Response response = qiNiuService.uploadFile(new File(localFilePath));
			if (response.isOK()) {
				JSONObject jsonObject = JSONUtil.parseObj(response.bodyString());

				String yunFileName = jsonObject.getStr("key");
				String yunFilePath = StrUtil.appendIfMissing(prefix, "/") + yunFileName;

				FileUtil.del(new File(localFilePath));

				log.info("【文件上传至七牛云】绝对路径：{}", yunFilePath);
				return Dict.create().set("code", 200).set("message", "上传成功").set("data", Dict.create().set("fileName", yunFileName).set("filePath", yunFilePath));
			} else {
				log.error("【文件上传至七牛云】失败，{}", JSONUtil.toJsonStr(response));
				FileUtil.del(new File(localFilePath));
				return Dict.create().set("code", 500).set("message", "文件上传失败");
			}
		} catch (IOException e) {
			log.error("【文件上传至七牛云】失败，绝对路径：{}", localFilePath);
			return Dict.create().set("code", 500).set("message", "文件上传失败");
		}
	}