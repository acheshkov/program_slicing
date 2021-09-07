private List<PropertyAccessor> getPropertyAccessorsToTry(
			@Nullable Object contextObject, List<PropertyAccessor> propertyAccessors) {

		Class<?> targetType = (contextObject != null ? contextObject.getClass() : null);

		List<PropertyAccessor> specificAccessors = new ArrayList<>();
		List<PropertyAccessor> generalAccessors = new ArrayList<>();
		for (PropertyAccessor resolver : propertyAccessors) {
			Class<?>[] targets = resolver.getSpecificTargetClasses();
			if (targets == null) {
				// generic resolver that says it can be used for any type
				generalAccessors.add(resolver);
			}
			else if (targetType != null) {
				for (Class<?> clazz : targets) {
					if (clazz == targetType) {
						specificAccessors.add(resolver);
						break;
					}
					else if (clazz.isAssignableFrom(targetType)) {
						generalAccessors.add(resolver);
					}
				}
			}
		}
		List<PropertyAccessor> resolvers = new ArrayList<>(specificAccessors);
		generalAccessors.removeAll(specificAccessors);
		resolvers.addAll(generalAccessors);
		return resolvers;
	}