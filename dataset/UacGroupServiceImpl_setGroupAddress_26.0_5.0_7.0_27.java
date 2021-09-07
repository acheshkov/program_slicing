private void setGroupAddress(UacGroup uacGroup) {
		List<Long> addressList = uacGroup.getAddressList();
		Preconditions.checkArgument(!PublicUtil.isEmpty(addressList), "地址不能为空");
		Preconditions.checkArgument(addressList.size() >= GlobalConstant.TWO_INT, "地址至少选两级");

		StringBuilder groupAddress = new StringBuilder();
		int level = 0;
		for (Long addressId : addressList) {
			// 根据地址ID获取地址名称
			String addressName = mdcAddressService.getAddressById(addressId).getName();
			if (level == 0) {
				uacGroup.setProvinceId(addressId);
				uacGroup.setProvinceName(addressName);
			} else if (level == 1) {
				uacGroup.setCityId(addressId);
				uacGroup.setCityName(addressName);
			} else if (level == 2) {
				uacGroup.setAreaId(addressId);
				uacGroup.setAreaName(addressName);
			} else {
				uacGroup.setStreetId(addressId);
				uacGroup.setStreetName(addressName);
			}
			groupAddress.append(addressName);
			level++;
		}
		uacGroup.setGroupAddress(groupAddress.toString());
	}